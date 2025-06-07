from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Optional
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
import logging
from app.db import models
from app.schemas import user as user_schema, document as doc_schema, token as token_schema
from app.security import hashing, auth
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.services import document_processor
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DAILY_UPLOAD_LIMIT = 5
DAILY_QUERY_LIMIT = 10

router = APIRouter()

def _check_and_reset_daily_limits(user: models.User, db: Session):
    """
    A helper function to check if the user's last activity was on a previous day.
    If so, it resets their daily counters. This is the core of the reset logic.
    """
    today = date.today()
    if user.last_activity_date and user.last_activity_date.date() < today:
        user.query_count = 0
        user.pdf_upload_count = 0

@router.post("/register", response_model=user_schema.User)
def register_new_user(user: user_schema.UserCreate, db: Session = Depends(auth.get_db)):
    """Register a new user with invite code validation."""
    invite_code = db.query(models.InviteCode).filter(models.InviteCode.code == user.invite_code).first()
    if not invite_code or invite_code.is_used:
        raise HTTPException(status_code=400, detail="Invalid or used invite code")

    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = hashing.Hasher.get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    invite_code.is_used = True
    db.add(invite_code)
    db.commit()
    db.refresh(new_user)
    logger.info(f"New user registered: {user.username}")
    return new_user


@router.post("/login", response_model=token_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    """User login endpoint."""
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not hashing.Hasher.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    logger.info(f"User logged in: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=user_schema.UserDetail)
def read_users_me(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    """
    Fetch the profile of the currently authenticated user.
    This also resets their daily limits if it's their first visit of the day.
    """
    _check_and_reset_daily_limits(current_user, db)
    db.commit()
    db.refresh(current_user)
    return current_user
@router.post("/documents/upload", response_model=doc_schema.Document)
def upload_document(
        file: UploadFile = File(...),
        db: Session = Depends(auth.get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    """
    Enhanced file upload with support for PDF and DOCX files, including advanced analysis.
    """
    try:
        _check_and_reset_daily_limits(current_user, db)
        if current_user.pdf_upload_count >= DAILY_UPLOAD_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily upload limit reached."
            )
        contents = file.file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="File is empty")
        validation_result = document_processor.validate_file_upload(contents, file.filename)
        if not validation_result["is_valid"]:
            raise HTTPException(status_code=400, detail=validation_result["error_message"])

        logger.info(
            f"Processing {validation_result['file_type']} file: {file.filename} ({validation_result['file_size']} bytes)")
        upload_success = document_processor.upload_file_to_gcs(
            file_contents=contents,
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream"
        )

        if not upload_success:
            logger.warning(f"GCS upload failed for {file.filename}, continuing with local processing")
        try:
            if hasattr(document_processor, 'determine_file_type_and_extract_advanced'):
                extracted_text, metadata, analysis = document_processor.determine_file_type_and_extract_advanced(
                    contents, file.filename
                )
                logger.info(
                    f"Advanced extraction successful: {metadata.word_count} words, {metadata.document_type.value}")
                if hasattr(document_processor, 'upload_file_to_gcs_with_metadata'):
                    document_processor.upload_file_to_gcs_with_metadata(
                        contents, file.filename, file.content_type or "application/octet-stream", metadata
                    )

            else:
                extracted_text = document_processor.determine_file_type_and_extract(contents, file.filename)
                logger.info(f"Basic extraction successful: {len(extracted_text.split())} words")
                metadata = None
                analysis = None

        except ValueError as e:
            logger.error(f"Text extraction failed for {file.filename}: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error during text extraction for {file.filename}: {str(e)}")
            raise HTTPException(status_code=500,
                                detail=f"An unexpected error occurred during text extraction: {str(e)}")

        if hasattr(document_processor, 'preprocess_text'):
            extracted_text = document_processor.preprocess_text(extracted_text)
        new_document = models.Document(
            filename=file.filename,
            content=extracted_text,
            owner=current_user
        )

        if metadata and hasattr(new_document, 'metadata'):
            new_document.metadata = {
                'file_type': metadata.file_type,
                'word_count': metadata.word_count,
                'language_primary': metadata.language_primary,
                'document_type': metadata.document_type.value,
                'complexity_level': metadata.complexity_level.value,
                'confidence_score': metadata.confidence_score,
                'processing_timestamp': datetime.utcnow().isoformat()
            }

        db.add(new_document)

        current_user.pdf_upload_count += 1
        current_user.last_activity_date = datetime.utcnow()
        db.add(current_user)
        db.commit()
        db.refresh(new_document)

        logger.info(f"Document uploaded successfully: {file.filename} for user {current_user.username}")
        return new_document

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_document: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during file upload")


@router.get("/documents", response_model=List[doc_schema.Document])
def list_user_documents(current_user: models.User = Depends(auth.get_current_user)):
    """List all documents for the current user."""
    return current_user.documents


@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
        doc_id: int,
        db: Session = Depends(auth.get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    """Delete a specific document."""
    doc_to_delete = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    if doc_to_delete.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this document."
        )
    deletion_success = document_processor.delete_file_from_gcs(doc_to_delete.filename)
    if not deletion_success:
        logger.warning(f"Failed to delete {doc_to_delete.filename} from GCS, continuing with database deletion")

    db.delete(doc_to_delete)
    db.commit()

    logger.info(f"Document deleted: {doc_to_delete.filename} by user {current_user.username}")
    return
@router.post("/query", response_model=doc_schema.QueryResponse)
def perform_rag_query(
        query: doc_schema.QueryRequest,
        db: Session = Depends(auth.get_db),
        current_user: models.User = Depends(auth.get_current_user)
):
    """
    Enhanced RAG query with advanced document understanding and friendly personality.
    """
    try:
        _check_and_reset_daily_limits(current_user, db)
        if current_user.query_count >= DAILY_QUERY_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily query limit reached."
            )
        if not query.question or not query.question.strip():
            raise HTTPException(status_code=400, detail="Query question cannot be empty")
        user_documents = current_user.documents
        if not user_documents:
            raise HTTPException(
                status_code=404,
                detail="No documents found. Please upload a document first."
            )
        context = "\n\n".join([doc.content for doc in user_documents])
        source_filenames = [doc.filename for doc in user_documents]
        latest_filename = source_filenames[0] if source_filenames else None

        logger.info(f"Processing query from user {current_user.username}: '{query.question[:50]}...'")
        try:
            if hasattr(document_processor, 'generate_answer_with_ultra_rag'):
                answer = document_processor.generate_answer_with_ultra_rag(
                    question=query.question,
                    context=context,
                    filename=latest_filename
                )
                logger.info("Used ultra-advanced RAG processing")

            elif hasattr(document_processor, 'generate_answer_with_rag'):
                answer = document_processor.generate_answer_with_rag(
                    question=query.question,
                    context=context
                )
                logger.info("Used standard RAG processing")

            else:
                raise HTTPException(
                    status_code=500,
                    detail="RAG processing functionality not available"
                )

        except Exception as e:
            logger.error(f"RAG processing error: {str(e)}")
            answer = f"""
I apologize, but I encountered an error while processing your question: "{query.question}"

This might be due to:
- Complex document structure that needs manual review
- Temporary processing issues
- Very large document content

Please try:
1. Rephrasing your question more specifically
2. Asking about a particular section of the document
3. Trying again in a few moments

Your uploaded documents contain information about: {', '.join(source_filenames)}

I'm here to help once the issue is resolved! 😊
"""
        current_user.query_count += 1
        current_user.last_activity_date = datetime.utcnow()
        db.add(current_user)
        db.commit()

        logger.info(f"Query processed successfully for user {current_user.username}")

        return doc_schema.QueryResponse(
            answer=answer,
            source_documents=source_filenames
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in perform_rag_query: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your query"
        )

@router.get("/documents/{doc_id}/info")
def get_document_info(
        doc_id: int,
        current_user: models.User = Depends(auth.get_current_user),
        db: Session = Depends(auth.get_db)
):
    """Get detailed information about a specific document."""
    document = db.query(models.Document).filter(
        models.Document.id == doc_id,
        models.Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    doc_info = {
        "filename": document.filename,
        "upload_date": document.created_at,
        "word_count": len(document.content.split()) if document.content else 0,
        "character_count": len(document.content) if document.content else 0,
    }
    if hasattr(document, 'metadata') and document.metadata:
        doc_info.update(document.metadata)
    if hasattr(document_processor, 'get_file_info_from_gcs'):
        gcs_info = document_processor.get_file_info_from_gcs(document.filename)
        if gcs_info:
            doc_info["gcs_info"] = gcs_info

    return doc_info


@router.get("/system/status")
def get_system_status():
    """Get system status and available features."""
    available_features = {
        "basic_text_extraction": hasattr(document_processor, 'extract_text_from_pdf'),
        "advanced_text_extraction": hasattr(document_processor, 'extract_text_from_pdf_advanced'),
        "docx_support": hasattr(document_processor, 'extract_text_from_docx'),
        "ultra_rag": hasattr(document_processor, 'generate_answer_with_ultra_rag'),
        "friendly_responses": hasattr(document_processor, 'generate_friendly_greeting_response'),
        "document_analysis": hasattr(document_processor, 'analyze_document_structure'),
        "file_validation": hasattr(document_processor, 'validate_file_upload'),
        "gcs_storage": hasattr(document_processor, 'upload_file_to_gcs'),
        "enhanced_metadata": hasattr(document_processor, 'upload_file_to_gcs_with_metadata')
    }

    return {
        "status": "operational",
        "features": available_features,
        "supported_formats": ["PDF", "DOCX"],
        "daily_limits": {
            "uploads": DAILY_UPLOAD_LIMIT,
            "queries": DAILY_QUERY_LIMIT
        }
    }
