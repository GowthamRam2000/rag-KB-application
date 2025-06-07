import fitz
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Tuple, Dict, Any, List, Optional
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import re
import json
from datetime import datetime
import hashlib
from dataclasses import dataclass
from enum import Enum
import logging
from app.core.config import INSTANCE_CONNECTION_NAME
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
PROJECT_ID = INSTANCE_CONNECTION_NAME.split(':')[0]
BUCKET_NAME = 'your bucket name'
LOCATION = 'us'

try:
    storage_client = storage.Client(project=PROJECT_ID)
    logger.info("Successfully initialized Google Cloud Storage client")
except Exception as e:
    logger.error(f"Failed to initialize storage client: {e}")
    storage_client = None
class DocumentType(Enum):
    ACADEMIC_PAPER = "academic_paper"
    LEGAL_CONTRACT = "legal_contract"
    FINANCIAL_REPORT = "financial_report"
    TECHNICAL_MANUAL = "technical_manual"
    POLICY_DOCUMENT = "policy_document"
    MEDICAL_RECORD = "medical_record"
    BUSINESS_PROPOSAL = "business_proposal"
    RESEARCH_REPORT = "research_report"
    REGULATORY_FILING = "regulatory_filing"
    EDUCATIONAL_MATERIAL = "educational_material"
    NEWS_ARTICLE = "news_article"
    GENERAL_DOCUMENT = "general_document"
class ContentComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    HIGHLY_TECHNICAL = "highly_technical"
    SPECIALIZED = "specialized"
@dataclass
class DocumentMetadata:
    file_type: str
    estimated_pages: int
    word_count: int
    language_primary: str
    languages_detected: List[str]
    document_type: DocumentType
    complexity_level: ContentComplexity
    key_topics: List[str]
    entities_detected: List[str]
    structure_analysis: Dict[str, Any]
    confidence_score: float

@dataclass
class SemanticChunk:
    content: str
    chunk_type: str
    importance_score: float
    topic_tags: List[str]
    entities: List[str]
    relationships: List[str]
    context_window: str
def upload_file_to_gcs(file_contents: bytes, filename: str, content_type: str):
    if not storage_client:
        logger.error("Storage client not initialized")
        return False
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.metadata = {
            'content_type': content_type,
            'upload_timestamp': datetime.now().isoformat(),
            'file_size': str(len(file_contents)),
            'processed': 'true'
        }
        blob.upload_from_string(file_contents, content_type=content_type)
        logger.info(f"Successfully uploaded {filename} to GCS with metadata.")
        return True
    except Exception as e:
        logger.error(f"Failed to upload to GCS: {e}")
        return False
def upload_file_to_gcs_with_metadata(file_contents: bytes, filename: str, content_type: str,
                                     metadata: DocumentMetadata):
    if not storage_client:
        logger.error("Storage client not initialized")
        return False
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.metadata = {
            'document_type': metadata.document_type.value,
            'complexity_level': metadata.complexity_level.value,
            'primary_language': metadata.language_primary,
            'word_count': str(metadata.word_count),
            'confidence_score': str(metadata.confidence_score),
            'processing_timestamp': datetime.now().isoformat()
        }

        blob.upload_from_string(file_contents, content_type=content_type)
        logger.info(f"Successfully uploaded {filename} with metadata to GCS.")
        return True
    except Exception as e:
        logger.error(f"Failed to upload to GCS with metadata: {e}")
        return False
def extract_text_from_pdf(file_contents: bytes) -> str:
    if not file_contents:
        raise ValueError("No file contents provided")
    text = ""
    try:
        with fitz.open(stream=file_contents, filetype="pdf") as doc:
            if len(doc) == 0:
                raise ValueError("PDF document is empty")

            for page_num, page in enumerate(doc):
                if page_num > 0:
                    text += f"\n\n--- Page {page_num + 1} ---\n\n"
                page_text = page.get_text("text", sort=True)
                if not page_text.strip():
                    continue
                lines = page_text.split('\n')
                processed_lines = []
                for i, line in enumerate(lines):
                    cleaned_line = ' '.join(line.split())
                    if not cleaned_line:
                        continue
                    if (len(cleaned_line) < 100 and
                            (cleaned_line.isupper() or
                             (i < len(lines) - 1 and not lines[i + 1].strip()))):
                        processed_lines.append(f"\n## {cleaned_line}\n")
                    else:
                        processed_lines.append(cleaned_line)

                text += '\n'.join(processed_lines)
        result_text = text.strip()
        if not result_text:
            raise ValueError("No extractable text found in PDF")
        logger.info("Successfully extracted text from PDF with enhanced formatting.")
        return result_text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise ValueError(f"Could not parse the provided PDF file: {e}")
def extract_text_from_pdf_advanced(file_contents: bytes) -> Tuple[str, DocumentMetadata]:
    text = ""
    metadata_info = {
        "pages": 0,
        "images": 0,
        "tables": 0,
        "fonts": set(),
        "languages": set(),
        "structure_elements": []
    }

    try:
        with fitz.open(stream=file_contents, filetype="pdf") as doc:
            metadata_info["pages"] = len(doc)
            for page_num, page in enumerate(doc):
                text_dict = page.get_text("dict")
                blocks = text_dict.get("blocks", [])
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                font_info = f"{span.get('font', 'unknown')}_{span.get('size', 0)}"
                                metadata_info["fonts"].add(font_info)
                                text_content = span.get("text", "")
                                if any(ord(char) > 127 for char in text_content):
                                    metadata_info["languages"].add("non_latin")
                page_text = page.get_text()
                if page_num > 0:
                    text += f"\n\n{'=' * 50}\n📄 PAGE {page_num + 1}\n{'=' * 50}\n\n"
                lines = page_text.split('\n')
                processed_lines = []
                for i, line in enumerate(lines):
                    cleaned_line = ' '.join(line.split())
                    if not cleaned_line:
                        continue
                    if (len(cleaned_line) < 100 and
                            cleaned_line.isupper() or
                            (i < len(lines) - 1 and not lines[i + 1].strip())):
                        processed_lines.append(f"\n## {cleaned_line}\n")
                        metadata_info["structure_elements"].append(f"header:{cleaned_line}")
                    else:
                        processed_lines.append(cleaned_line)

                text += '\n'.join(processed_lines)
                if page.search_for("table") or page.search_for("Table"):
                    metadata_info["tables"] += 1

                image_list = page.get_images()
                metadata_info["images"] += len(image_list)
        word_count = len(text.split())
        primary_lang = detect_primary_language(text)
        doc_type = classify_document_type(text)
        complexity = assess_content_complexity(text)
        topics = extract_key_topics(text)
        entities = extract_named_entities(text)
        metadata = DocumentMetadata(
            file_type="pdf",
            estimated_pages=metadata_info["pages"],
            word_count=word_count,
            language_primary=primary_lang,
            languages_detected=list(metadata_info["languages"]),
            document_type=doc_type,
            complexity_level=complexity,
            key_topics=topics,
            entities_detected=entities,
            structure_analysis=metadata_info,
            confidence_score=calculate_extraction_confidence(text, metadata_info)
        )
        return text.strip(), metadata
    except Exception as e:
        logger.error(f"Advanced PDF extraction failed: {e}")
        raise ValueError(f"Could not parse the provided PDF file: {e}")
def extract_text_from_docx(file_contents: bytes) -> str:
    if not file_contents:
        raise ValueError("No file contents provided")
    try:
        with zipfile.ZipFile(BytesIO(file_contents)) as docx:
            if 'word/document.xml' not in docx.namelist():
                raise ValueError("Invalid DOCX file: missing document.xml")

            tree = ET.fromstring(docx.read('word/document.xml'))
            namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            text_elements = []
            for paragraph in tree.findall('.//w:p', namespace):
                para_text = ""
                is_header = False
                style_elem = paragraph.find('.//w:pStyle', namespace)
                if style_elem is not None:
                    style_val = style_elem.get(f'{{{namespace["w"]}}}val', '')
                    if 'heading' in style_val.lower() or 'title' in style_val.lower():
                        is_header = True
                for run in paragraph.findall('.//w:r', namespace):
                    for text_elem in run.findall('.//w:t', namespace):
                        if text_elem.text:
                            para_text += text_elem.text

                if para_text.strip():
                    if is_header:
                        text_elements.append(f"\n## {para_text.strip()}\n")
                    else:
                        text_elements.append(para_text.strip())
            tables = tree.findall('.//w:tbl', namespace)
            for table in tables:
                table_text = "\n### TABLE CONTENT ###\n"
                for row in table.findall('.//w:tr', namespace):
                    row_text = []
                    for cell in row.findall('.//w:tc', namespace):
                        cell_text = ""
                        for para in cell.findall('.//w:p', namespace):
                            for text_elem in para.findall('.//w:t', namespace):
                                if text_elem.text:
                                    cell_text += text_elem.text
                        row_text.append(cell_text.strip())
                    table_text += " | ".join(row_text) + "\n"
                text_elements.append(table_text)

            result_text = '\n\n'.join(text_elements)
            if not result_text.strip():
                raise ValueError("No text content found in DOCX")
            logger.info("Successfully extracted text from DOCX with structure preservation.")
            return result_text

    except zipfile.BadZipFile:
        raise ValueError("Invalid DOCX file format")
    except ET.ParseError:
        raise ValueError("Could not parse DOCX document structure")
    except Exception as e:
        logger.error(f"Failed to extract text from DOCX: {e}")
        raise ValueError(f"Could not parse the provided Word document: {e}")


def extract_text_from_docx_advanced(file_contents: bytes) -> Tuple[str, DocumentMetadata]:
    try:
        with zipfile.ZipFile(BytesIO(file_contents), 'r') as docx_zip:
            document_xml = docx_zip.read('word/document.xml')
            try:
                styles_xml = docx_zip.read('word/styles.xml')
                styles_root = ET.fromstring(styles_xml)
            except:
                styles_root = None
            root = ET.fromstring(document_xml)
            namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

            text_elements = []
            structure_info = {
                "paragraphs": 0,
                "tables": 0,
                "headers": 0,
                "lists": 0
            }
            for paragraph in root.findall('.//w:p', namespace):
                para_text = ""
                is_header = False
                style_elem = paragraph.find('.//w:pStyle', namespace)
                if style_elem is not None:
                    style_val = style_elem.get(f'{{{namespace["w"]}}}val', '')
                    if 'heading' in style_val.lower() or 'title' in style_val.lower():
                        is_header = True
                        structure_info["headers"] += 1
                for run in paragraph.findall('.//w:r', namespace):
                    for text_elem in run.findall('.//w:t', namespace):
                        if text_elem.text:
                            para_text += text_elem.text

                if para_text.strip():
                    if is_header:
                        text_elements.append(f"\n## {para_text.strip()}\n")
                    else:
                        text_elements.append(para_text.strip())
                    structure_info["paragraphs"] += 1
            tables = root.findall('.//w:tbl', namespace)
            structure_info["tables"] = len(tables)
            for table in tables:
                table_text = "\n### TABLE CONTENT ###\n"
                for row in table.findall('.//w:tr', namespace):
                    row_text = []
                    for cell in row.findall('.//w:tc', namespace):
                        cell_text = ""
                        for para in cell.findall('.//w:p', namespace):
                            for text_elem in para.findall('.//w:t', namespace):
                                if text_elem.text:
                                    cell_text += text_elem.text
                        row_text.append(cell_text.strip())
                    table_text += " | ".join(row_text) + "\n"
                text_elements.append(table_text)

            extracted_text = '\n\n'.join(text_elements)
            word_count = len(extracted_text.split())
            primary_lang = detect_primary_language(extracted_text)
            doc_type = classify_document_type(extracted_text)
            complexity = assess_content_complexity(extracted_text)
            topics = extract_key_topics(extracted_text)
            entities = extract_named_entities(extracted_text)

            metadata = DocumentMetadata(
                file_type="docx",
                estimated_pages=max(1, word_count // 250),
                word_count=word_count,
                language_primary=primary_lang,
                languages_detected=[primary_lang],
                document_type=doc_type,
                complexity_level=complexity,
                key_topics=topics,
                entities_detected=entities,
                structure_analysis=structure_info,
                confidence_score=calculate_extraction_confidence(extracted_text, structure_info)
            )
            return extracted_text, metadata
    except Exception as e:
        logger.error(f"Advanced DOCX extraction failed: {e}")
        raise ValueError(f"Could not parse the provided Word document: {e}")


def determine_file_type_and_extract(file_contents: bytes, filename: str) -> str:
    if not file_contents:
        raise ValueError("No file contents provided")
    if not filename:
        raise ValueError("No filename provided")
    max_size = 50 * 1024 * 1024
    if len(file_contents) > max_size:
        raise ValueError("File size exceeds 50MB limit")
    filename_lower = filename.lower()
    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_contents)
    elif filename_lower.endswith('.docx'):
        return extract_text_from_docx(file_contents)
    else:
        raise ValueError("Unsupported file format. Please upload PDF or DOCX files only.")
def determine_file_type_and_extract_advanced(file_contents: bytes, filename: str) -> Tuple[
    str, DocumentMetadata, Dict[str, Any]]:
    filename_lower = filename.lower()

    try:
        if filename_lower.endswith('.pdf'):
            text, metadata = extract_text_from_pdf_advanced(file_contents)
        elif filename_lower.endswith('.docx'):
            text, metadata = extract_text_from_docx_advanced(file_contents)
        elif filename_lower.endswith('.doc'):
            raise ValueError("Legacy .doc files require conversion to .docx format for optimal processing.")
        else:
            raise ValueError("Unsupported file format. Please upload PDF or DOCX files.")
        analysis = perform_comprehensive_document_analysis(text, metadata)
        return text, metadata, analysis
    except Exception as e:
        logger.error(f"Advanced file processing failed: {e}")
        raise
def detect_primary_language(text: str) -> str:
    if not text:
        return "English"
    text_sample = text[:1000].lower()
    hindi_indicators = ['के', 'का', 'की', 'में', 'से', 'को', 'और', 'है', 'हैं', 'आवास', 'दर']
    spanish_indicators = ['el', 'la', 'los', 'las', 'de', 'en', 'y', 'que', 'para', 'con']
    french_indicators = ['le', 'la', 'les', 'de', 'et', 'en', 'un', 'une', 'pour', 'avec']
    german_indicators = ['der', 'die', 'das', 'und', 'in', 'zu', 'den', 'von', 'mit', 'für']
    hindi_count = sum(1 for word in hindi_indicators if word in text_sample)
    spanish_count = sum(1 for word in spanish_indicators if word in text_sample)
    french_count = sum(1 for word in french_indicators if word in text_sample)
    german_count = sum(1 for word in german_indicators if word in text_sample)
    if hindi_count > 2:
        return "Hindi/Hinglish"
    elif spanish_count > 3:
        return "Spanish"
    elif french_count > 3:
        return "French"
    elif german_count > 3:
        return "German"
    else:
        return "English"
def classify_document_type(text: str) -> DocumentType:
    text_lower = text.lower()
    academic_terms = ['abstract', 'methodology', 'literature review', 'hypothesis', 'conclusion', 'references',
                      'citation']
    legal_terms = ['whereas', 'party', 'agreement', 'contract', 'terms and conditions', 'liability', 'jurisdiction']
    financial_terms = ['revenue', 'profit', 'loss', 'balance sheet', 'cash flow', 'assets', 'liabilities', 'equity']
    technical_terms = ['procedure', 'specification', 'installation', 'configuration', 'troubleshooting', 'manual']
    policy_terms = ['policy', 'guideline', 'procedure', 'compliance', 'regulation', 'requirement', 'entitlement']
    medical_terms = ['patient', 'diagnosis', 'treatment', 'medication', 'symptoms', 'medical history', 'prescription']
    scores = {
        DocumentType.ACADEMIC_PAPER: sum(1 for term in academic_terms if term in text_lower),
        DocumentType.LEGAL_CONTRACT: sum(1 for term in legal_terms if term in text_lower),
        DocumentType.FINANCIAL_REPORT: sum(1 for term in financial_terms if term in text_lower),
        DocumentType.TECHNICAL_MANUAL: sum(1 for term in technical_terms if term in text_lower),
        DocumentType.POLICY_DOCUMENT: sum(1 for term in policy_terms if term in text_lower),
        DocumentType.MEDICAL_RECORD: sum(1 for term in medical_terms if term in text_lower)
    }
    max_score = max(scores.values())
    if max_score >= 2:
        return max(scores, key=scores.get)
    else:
        return DocumentType.GENERAL_DOCUMENT
def assess_content_complexity(text: str) -> ContentComplexity:
    sentences = text.split('.')
    avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
    technical_terms = ['algorithm', 'methodology', 'implementation', 'specification', 'configuration',
                       'optimization', 'analysis', 'framework', 'architecture', 'infrastructure']
    specialized_terms = ['pursuant', 'heretofore', 'notwithstanding', 'aforementioned', 'whereby',
                         'coefficient', 'derivative', 'integral', 'hypothesis', 'paradigm']
    technical_count = sum(1 for term in technical_terms if term.lower() in text.lower())
    specialized_count = sum(1 for term in specialized_terms if term.lower() in text.lower())
    complexity_score = 0
    if avg_sentence_length > 25:
        complexity_score += 2
    elif avg_sentence_length > 20:
        complexity_score += 1
    complexity_score += min(technical_count // 5, 2)
    complexity_score += min(specialized_count // 3, 3)
    if complexity_score >= 6:
        return ContentComplexity.SPECIALIZED
    elif complexity_score >= 4:
        return ContentComplexity.HIGHLY_TECHNICAL
    elif complexity_score >= 2:
        return ContentComplexity.COMPLEX
    elif complexity_score >= 1:
        return ContentComplexity.MODERATE
    else:
        return ContentComplexity.SIMPLE
def extract_key_topics(text: str) -> List[str]:
    if not text:
        return []
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    stop_words = {'that', 'this', 'with', 'from', 'they', 'been', 'have', 'were', 'said', 'each', 'which', 'their',
                  'time', 'will', 'about', 'would', 'there', 'could', 'other', 'more', 'very', 'what', 'know', 'just',
                  'first', 'into', 'over', 'think', 'also', 'your', 'work', 'life', 'only', 'can', 'still', 'should',
                  'after', 'being', 'now', 'made', 'before', 'here', 'through', 'when', 'where', 'much', 'some',
                  'these', 'many', 'then', 'them', 'well', 'were'}
    filtered_words = [word for word in words if word not in stop_words and len(word) > 4]
    word_freq = {}
    for word in filtered_words:
        word_freq[word] = word_freq.get(word, 0) + 1
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:10] if freq > 1]


def extract_named_entities(text: str) -> List[str]:
    if not text:
        return []
    entities = []
    date_patterns = [
        r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
        r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b',
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
    ]

    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities.extend([f"DATE:{match}" for match in matches[:5]]) 
    money_patterns = [
        r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
        r'₹\d+(?:,\d{3})*(?:\.\d{2})?',
        r'\b\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|INR|EUR|GBP)\b'
    ]

    for pattern in money_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities.extend([f"MONEY:{match}" for match in matches[:5]])
    org_patterns = [
        r'\b[A-Z][a-z]+ (?:Inc|Corp|LLC|Ltd|Company|Corporation|Limited)\b',
        r'\b[A-Z]{2,}\b' 
    ]

    for pattern in org_patterns:
        matches = re.findall(pattern, text)
        entities.extend([f"ORG:{match}" for match in matches[:5]])

    return list(set(entities))[:20]
def calculate_extraction_confidence(text: str, structure_info: Dict) -> float:
    confidence = 0.5
    if len(text) > 1000:
        confidence += 0.2
    elif len(text) > 500:
        confidence += 0.1
    if structure_info.get("paragraphs", 0) > 5:
        confidence += 0.1
    if structure_info.get("headers", 0) > 0:
        confidence += 0.1
    if len(text.split()) > 100:
        confidence += 0.1

    return min(confidence, 1.0)


def analyze_document_structure(context: str) -> Dict[str, Any]:
    if not context or not context.strip():
        return {
            "has_tables": False,
            "has_policies": False,
            "has_locations": False,
            "is_multilingual": False,
            "primary_language": "English",
            "word_count": 0,
            "confidence": 0.0,
            "document_type": "unknown",
            "key_topics": [],
            "entities": []
        }

    analysis = {
        "has_tables": False,
        "has_policies": False,
        "has_locations": False,
        "is_multilingual": False,
        "primary_language": "English",
        "word_count": len(context.split()),
        "confidence": 1.0,
        "document_type": "general",
        "key_topics": [],
        "entities": []
    }

    context_lower = context.lower()
    table_indicators = ["rate", "cost", "zone", "tier", "level", "grade", "$", "₹", "allowance",
                        "amount", "price", "fee", "charge", "expense", "budget"]
    policy_indicators = ["policy", "procedure", "guideline", "rule", "entitlement", "shall",
                         "must", "required", "mandatory", "compliance", "regulation"]
    location_indicators = ["zone", "region", "city", "country", "state", "province",
                           "new york", "delhi", "london", "mumbai", "bangalore", "chennai"]
    hindi_indicators = ['के लिए', 'में', 'क्या', 'है', 'दर', 'और', 'का', 'की', 'से', 'पर']
    if any(indicator in context_lower for indicator in table_indicators):
        analysis["has_tables"] = True

    if any(indicator in context_lower for indicator in policy_indicators):
        analysis["has_policies"] = True

    if any(indicator in context_lower for indicator in location_indicators):
        analysis["has_locations"] = True

    if any(indicator in context for indicator in hindi_indicators):
        analysis["is_multilingual"] = True
        analysis["primary_language"] = "Hindi/Hinglish"
    analysis["primary_language"] = detect_primary_language(context)
    analysis["document_type"] = classify_document_type(context).value
    analysis["key_topics"] = extract_key_topics(context)
    analysis["entities"] = extract_named_entities(context)
    if analysis["word_count"] < 50:
        analysis["confidence"] = 0.5
    elif analysis["word_count"] < 200:
        analysis["confidence"] = 0.7
    else:
        analysis["confidence"] = 1.0

    return analysis
def perform_comprehensive_document_analysis(text: str, metadata: DocumentMetadata) -> Dict[str, Any]:
    analysis = {
        "document_metadata": metadata.__dict__,
        "content_structure": analyze_content_structure(text),
        "semantic_analysis": perform_semantic_analysis(text),
        "knowledge_domains": identify_knowledge_domains(text),
        "cross_references": find_cross_references(text),
        "data_patterns": identify_data_patterns(text),
        "contextual_relationships": map_contextual_relationships(text),
        "inference_opportunities": identify_inference_opportunities(text, metadata)
    }

    return analysis
def analyze_content_structure(text: str) -> Dict[str, Any]:
    structure = {
        "sections": [],
        "subsections": [],
        "lists": [],
        "tables": [],
        "figures": [],
        "appendices": [],
        "hierarchical_depth": 0,
        "content_flow": []
    }

    lines = text.split('\n')
    current_section = None

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if line.startswith('##') or line.isupper() and len(line) < 100:
            structure["sections"].append({
                "title": line.replace('##', '').strip(),
                "line_number": i,
                "content_preview": ' '.join(lines[i + 1:i + 3])
            })
            current_section = line.replace('##', '').strip()
        if line.startswith(('-', '*', '•')) or re.match(r'^\d+\.', line):
            structure["lists"].append({
                "type": "ordered" if re.match(r'^\d+\.', line) else "unordered",
                "content": line,
                "section": current_section
            })
        if 'table' in line.lower() or '|' in line:
            structure["tables"].append({
                "indicator": line,
                "line_number": i,
                "section": current_section
            })

    structure["hierarchical_depth"] = len(structure["sections"])
    return structure


def perform_semantic_analysis(text: str) -> Dict[str, Any]:
    semantic_info = {
        "key_concepts": [],
        "concept_relationships": [],
        "semantic_density": 0,
        "topic_coherence": 0,
        "information_layers": []
    }
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    concept_candidates = []
    for sentence in sentences:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', sentence.lower())
        # Look for noun phrases and important terms
        for i, word in enumerate(words):
            if word in ['policy', 'procedure', 'requirement', 'allowance', 'rate', 'grade', 'level']:
                context = ' '.join(words[max(0, i - 2):i + 3])
                concept_candidates.append({
                    "concept": word,
                    "context": context,
                    "sentence": sentence
                })

    semantic_info["key_concepts"] = concept_candidates[:15]
    semantic_info["semantic_density"] = len(concept_candidates) / len(sentences) if sentences else 0

    return semantic_info
def identify_knowledge_domains(text: str) -> List[str]:
    domains = []
    text_lower = text.lower()

    domain_indicators = {
        "Human Resources": ["hr", "employee", "salary", "benefits", "leave", "performance", "recruitment"],
        "Finance": ["budget", "cost", "revenue", "profit", "expense", "financial", "accounting"],
        "Legal": ["contract", "agreement", "legal", "compliance", "regulation", "law", "terms"],
        "Technology": ["system", "software", "hardware", "network", "database", "application", "technical"],
        "Healthcare": ["medical", "health", "patient", "treatment", "diagnosis", "clinical", "healthcare"],
        "Travel": ["travel", "trip", "accommodation", "transport", "per diem", "allowance", "lodging"],
        "Operations": ["process", "procedure", "workflow", "operation", "management", "quality", "standard"],
        "Research": ["research", "study", "analysis", "methodology", "findings", "data", "results"]
    }

    for domain, indicators in domain_indicators.items():
        score = sum(1 for indicator in indicators if indicator in text_lower)
        if score >= 2:
            domains.append(f"{domain} (confidence: {score})")

    return domains

def find_cross_references(text: str) -> List[Dict[str, str]]:
    references = []
    ref_patterns = [
        r'(?:see|refer to|as per|according to)\s+(?:section|chapter|table|figure|appendix)\s+(\w+)',
        r'(?:section|chapter|table|figure|appendix)\s+(\w+)\s+(?:shows|indicates|describes)',
        r'(?:above|below|following|preceding)\s+(?:section|table|figure)'
    ]

    for pattern in ref_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            references.append({
                "reference_text": match.group(0),
                "target": match.group(1) if match.groups() else "unspecified",
                "context": text[max(0, match.start() - 50):match.end() + 50]
            })

    return references


def identify_data_patterns(text: str) -> List[Dict[str, Any]]:
    patterns = []
    rate_pattern = r'(\w+(?:\s+\w+)*)\s*[:\-]\s*(?:₹|Rs\.?|\$|USD|INR)?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
    rate_matches = re.finditer(rate_pattern, text, re.IGNORECASE)

    for match in rate_matches:
        patterns.append({
            "type": "rate_pricing",
            "item": match.group(1).strip(),
            "value": match.group(2),
            "context": text[max(0, match.start() - 30):match.end() + 30]
        })
    grade_pattern = r'(L\d+|Level\s+\d+|Grade\s+\d+|Tier\s+\d+)'
    grade_matches = re.finditer(grade_pattern, text, re.IGNORECASE)
    for match in grade_matches:
        patterns.append({
            "type": "grade_level",
            "value": match.group(1),
            "context": text[max(0, match.start() - 30):match.end() + 30]
        })

    return patterns


def map_contextual_relationships(text: str) -> Dict[str, List[str]]:
    relationships = {
        "conditional": [],
        "causal": [],
        "temporal": [],
        "hierarchical": []
    }
    conditional_patterns = [
        r'if\s+(.+?)\s+then\s+(.+?)(?:\.|,)',
        r'provided\s+that\s+(.+?)(?:\.|,)',
        r'subject\s+to\s+(.+?)(?:\.|,)'
    ]

    for pattern in conditional_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            relationships["conditional"].append(match.group(0))
    causal_patterns = [
        r'because\s+(.+?)(?:\.|,)',
        r'due\s+to\s+(.+?)(?:\.|,)',
        r'as\s+a\s+result\s+of\s+(.+?)(?:\.|,)'
    ]

    for pattern in causal_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            relationships["causal"].append(match.group(0))

    return relationships


def identify_inference_opportunities(text: str, metadata: DocumentMetadata) -> List[Dict[str, str]]:
    opportunities = []
    if "rate" in text.lower() and "grade" in text.lower():
        opportunities.append({
            "type": "rate_calculation",
            "description": "Can infer rates for different grades based on patterns",
            "confidence": "high"
        })

    if "policy" in text.lower() and "exception" in text.lower():
        opportunities.append({
            "type": "exception_handling",
            "description": "Can infer exception scenarios based on policy rules",
            "confidence": "medium"
        })

    if metadata.document_type == DocumentType.POLICY_DOCUMENT:
        opportunities.append({
            "type": "compliance_inference",
            "description": "Can infer compliance requirements from policy statements",
            "confidence": "high"
        })

    return opportunities



def generate_friendly_greeting_response():
    return """
👋 Hello there! Great to see you here! 

I'm your friendly assistant, and I'm excited to help you navigate through your  policy documents. Think of me as your knowledgeable colleague who knows the policies inside and out! 😊

I'd love to help you find exactly what you're looking for. You can ask me anything about:



✨ **I'm here to make your  planning easier!** Just ask me anything about the documents, and I'll give you clear, helpful answers with all the details you need.

"""


def generate_off_topic_friendly_response(question: str):
    """Generate friendly response for off-topic questions."""
    question_lower = question.lower().strip()
    programming_keywords = ['program', 'code', 'function', 'algorithm', 'script', 'software', 'python', 'java',
                            'javascript', 'write', 'create', 'develop']
    if any(keyword in question_lower for keyword in programming_keywords) and 'travel' not in question_lower:
        return f"""
Thanks for thinking of me! 😊 While I'd love to help with programming, I'm actually your specialized  document assistant - think of me as the go-to expert for everything related to  policies and procedures!

I'm really passionate about helping with:
✈️ **Travel bookings and approvals**
💰 **Per diem and allowance calculations** 
🏨 **Accommodation guidelines**
🎫 **Flight class entitlements**
📋 **Exception request processes**
and helping you based on your uploaded documents 

Got any upcoming business trips planned? I'd be thrilled to help you understand your travel benefits and make sure you're getting everything you're entitled to!

What document-related question can I help you with today?
"""

    return f"""
I appreciate your question! 🌟 While I'd love to help with that, I'm specifically designed to be your document  expert. I'm like having a assistant  who knows every detail of the document that you have uploaded!

**Here's what I'm absolutely amazing at:**
🎯 **Travel allowances and rates**
📋 **Booking procedures and approvals**
🏨 **Accommodation guidelines**
✈️ **Flight entitlements by grade**
💼 **Business travel best practices**
and helping you based on your uploaded documents 

I'm here to make your business travel smooth, compliant, and cost-effective! 

What aspect of documents  can I help you explore today?
"""


def generate_vague_question_response():
    return """
I'm so glad you asked! 🌟 I'm your friendly travel policy companion, and I absolutely love helping colleagues navigate their business travel needs.

**Here's how I can make your travel planning awesome:**

🎯 **Quick Examples of What I'm Great At:**
- "What's the hotel allowance for L3 employees in Mumbai?"
- "Can I upgrade my flight if I pay the difference?"
- "How far in advance should I book my international travel?"
- "What's covered under the per diem for meals in London?"

💡 **Pro Tip**: The more specific your question, the more detailed and helpful my answer will be! I have access to all the latest policy details, rates, and procedures.

What aspect of business travel would you like to explore today? I'm here to help make your next trip smooth and compliant! ✈️
"""


def is_off_topic_request(question_lower: str) -> bool:
    off_topic_keywords = [
        'program', 'code', 'function', 'algorithm', 'script', 'software',
        'python', 'java', 'javascript', 'write', 'create', 'develop',
        'weather', 'news', 'sports', 'cooking', 'recipe', 'movie',
        'music', 'game', 'joke', 'story', 'math', 'calculate','c++','c','typescript','sql','nosql'
    ]

    travel_keywords = ['travel', 'trip', 'flight', 'hotel', 'accommodation', 'per diem', 'allowance', 'policy',
                       'booking']

    has_off_topic = any(keyword in question_lower for keyword in off_topic_keywords)
    has_travel = any(keyword in question_lower for keyword in travel_keywords)

    return has_off_topic and not has_travel


def is_vague_question(question_lower: str) -> bool:
    vague_patterns = [
        'help', 'what can you do', 'tell me', 'explain', 'info', 'information',
        'about', 'details', 'more', 'anything', 'everything'
    ]

    return (len(question_lower.split()) < 4 or
            any(pattern == question_lower for pattern in vague_patterns) or
            question_lower in ['what', 'how', 'why', 'when', 'where'])


def create_dynamic_ultra_prompt_with_personality(question: str, context: str, metadata: DocumentMetadata,
                                                 analysis: Dict[str, Any]) -> str:

    doc_type = metadata.document_type.value
    complexity = metadata.complexity_level.value
    primary_lang = metadata.language_primary
    key_topics = metadata.key_topics[:5]
    knowledge_domains = analysis.get("knowledge_domains", [])

    prompt = f"""
🧠 **UNIVERSAL DOCUMENT INTELLIGENCE SYSTEM v3.0**
**Advanced Multi-Modal Knowledge Synthesis Engine with Friendly Personality**

═══════════════════════════════════════════════════════════════════════════════════

**🎯 SYSTEM ROLE & CAPABILITIES:**

You are an elite AI system with PhD-level expertise across ALL domains, specializing in:
- **Document Intelligence**: Deep understanding of {doc_type} documents
- **Cross-Domain Knowledge**: Synthesis across {', '.join(knowledge_domains[:3])}
- **Multilingual Processing**: Native fluency in {primary_lang} and contextual languages
- **Inference Engine**: Advanced logical reasoning and pattern recognition
- **Knowledge Integration**: Seamless blending of document facts with world knowledge
- **Friendly Expertise**: Warm, approachable personality while maintaining professional excellence

**🤝 PERSONALITY & INTERACTION STYLE:**

**CORE PERSONALITY TRAITS:**
- **Warm & Approachable**: Use friendly, conversational tone while maintaining professionalism
- **Helpful & Enthusiastic**: Show genuine eagerness to assist with policy questions
- **Knowledgeable Guide**: Position as a trusted colleague who knows the policy thoroughly
- **Contextually Aware**: Recognize different types of questions and respond appropriately

**RESPONSE TONE GUIDELINES:**
- Start responses with enthusiasm ("Great question!" "I'd be happy to help!" "Excellent!")
- Use conversational transitions ("Here's what the policy says..." "Let me break this down for you...")
- Include helpful follow-ups ("Does this help?" "Any other document related questions?" "Need clarification on anything?")
- Use appropriate emojis sparingly but effectively (✈️ 💰 🏨 📋 🎯)
- End with encouraging, helpful closing statements

**🔬 DOCUMENT ANALYSIS PROFILE:**
Document Type: {doc_type.replace('_', ' ').title()}
Complexity Level: {complexity.title()}
Primary Language: {primary_lang}
Content Domains: {', '.join(knowledge_domains[:3])}
Key Topics: {', '.join(key_topics)}
Confidence Score: {metadata.confidence_score:.2f}
Structure Elements: {analysis.get('content_structure', {}).get('hierarchical_depth', 0)} sections

**🧬 ADVANCED REASONING PROTOCOLS:**

1. **HIERARCHICAL UNDERSTANDING**:
   - L1 encompasses L1-L8 range | Grade 5 includes Grades 1-10 | Senior includes all junior levels
   - Zone 1 includes Tier 1 cities | Metropolitan includes urban centers
   - Executive level spans Junior→Senior→Chief progression
   - Manager category includes Assistant→Senior→General Manager hierarchy

2. **GEOGRAPHIC INTELLIGENCE MATRIX**:
INDIA: Delhi/Mumbai/Bangalore → Zone 1 | Pune/Chennai → Zone 2 | Tier-2 cities → Zone 3
USA: NYC/SF/LA → Zone 1 | Chicago/Boston → Zone 2 | Regional → Zone 3
EUROPE: London/Paris/Frankfurt → Zone 1 | Regional capitals → Zone 2
APAC: Singapore/HK/Tokyo → Zone 1 | Regional hubs → Zone 2

3. **MULTILINGUAL SEMANTIC MAPPING**:
- Hindi: एल1 कैडर ↔ L1 cadre | दिल्ली ↔ Delhi | आवास दर ↔ accommodation rate
- Code-switching: Natural handling of mixed-language queries
- Cultural context: Understanding regional business practices and terminology

4. **DOMAIN-SPECIFIC EXPERTISE**:

**Travel Policies**: Per diem calculations, accommodation tiers, transport allowances, grade-based entitlements
**HR Policies**: Salary bands, leave entitlements, performance metrics, career progression
**Financial Documents**: Budget allocations, cost centers, revenue recognition, expense categories
**Legal Contracts**: Terms interpretation, liability clauses, compliance requirements
**Technical Manuals**: Procedures, specifications, troubleshooting, configuration guides
**Medical Records**: Diagnosis codes, treatment protocols, medication schedules, test results

5. **ADVANCED INFERENCE ENGINE**:
- **Pattern Recognition**: Identify implicit rules from explicit examples
- **Range Interpolation**: Calculate intermediate values from boundary conditions
- **Contextual Bridging**: Connect related concepts across document sections
- **Logical Extrapolation**: Extend policies to unstated but implied scenarios
- **Cross-Reference Resolution**: Link related information across document structure

**📊 DOCUMENT KNOWLEDGE BASE:**
{context}

**🎯 USER QUERY:**
"{question}"

**🚀 ULTRA-ADVANCED RESPONSE ARCHITECTURE:**

**PHASE 1: QUERY DECOMPOSITION & ANALYSIS**
- Parse query intent, entities, and context requirements
- Identify explicit vs. implicit information needs
- Map query to document structure and knowledge domains
- Determine inference requirements and confidence levels

**PHASE 2: MULTI-LAYERED INFORMATION RETRIEVAL**
- Extract direct facts from document knowledge base
- Identify related information through semantic relationships
- Map hierarchical and categorical relationships
- Cross-reference with domain-specific knowledge patterns

**PHASE 3: INTELLIGENT SYNTHESIS & INFERENCE**
- Apply domain expertise to interpret document facts
- Generate logical inferences based on established patterns
- Bridge information gaps using contextual understanding
- Validate inferences against document consistency

**PHASE 4: COMPREHENSIVE RESPONSE GENERATION WITH PERSONALITY**

**🎯 ENTHUSIASTIC OPENING**: 
Start with warm, encouraging language that shows excitement to help

**💡 DIRECT ANSWER**: 
Provide immediate, specific answer in user's preferred language with friendly explanations

**🔍 REASONING PATHWAY**: 
Explain the logical connections and inference steps in conversational tone

**📊 SUPPORTING EVIDENCE**: 
Present relevant data in optimal format with helpful context

**🌟 CONTEXTUAL ENRICHMENT**: 
Add valuable related information and practical implications

**🔗 KNOWLEDGE INTEGRATION**: 
Clearly distinguish document facts from expert knowledge synthesis

**🤝 HELPFUL CLOSING**: 
End with encouraging follow-up questions or offers for additional assistance

**⚡ ADVANCED FORMATTING INTELLIGENCE:**

- **Structured Data**: Use tables for rates, grades, comparisons, multi-dimensional data
- **Procedural Information**: Use numbered lists for step-by-step processes
- **Hierarchical Content**: Use nested formatting for complex relationships
- **Multilingual Responses**: Match user's language preference naturally
- **Visual Emphasis**: Use formatting to highlight critical information
- **Friendly Elements**: Include appropriate emojis and conversational markers

**🎨 RESPONSE QUALITY STANDARDS:**

1. **ACCURACY**: All specific data must originate from document - use expertise for interpretation only
2. **COMPLETENESS**: Address all aspects of the query with comprehensive coverage
3. **CLARITY**: Present complex information in accessible, well-structured format
4. **FRIENDLINESS**: Maintain warm, helpful tone throughout the response
5. **RELEVANCE**: Focus on information directly addressing user needs
6. **INTELLIGENCE**: Demonstrate sophisticated understanding through insightful connections
7. **TRANSPARENCY**: Clearly indicate when making inferences vs. stating facts

**🔄 SPECIALIZED SCENARIO HANDLING:**

**Complex Policy Queries**: Navigate multi-layered policy structures with enthusiastic explanations
**Cross-Reference Requests**: Link information across different document sections seamlessly with helpful context
**Calculation Requirements**: Perform accurate computations with step-by-step friendly explanations
**Exception Scenarios**: Address edge cases using policy principles with encouraging guidance
**Multilingual Queries**: Handle code-switching and cultural context with natural warmth
**Ambiguous Requests**: Seek clarification while providing best available interpretation with helpful suggestions

**⚡ EXECUTION DIRECTIVES:**

- **BE ENTHUSIASTIC**: Show genuine excitement about helping with travel policy questions
- **STAY CONVERSATIONAL**: Use natural, friendly language while maintaining expertise
- **NEVER ASSUME**: State clearly when information is not available, but do so helpfully
- **ALWAYS CONNECT**: Explicitly bridge user terminology with document terminology in friendly way
- **BE COMPREHENSIVE**: Provide valuable context beyond the minimum answer with enthusiasm
- **STAY GROUNDED**: Distinguish between document facts and expert interpretation clearly
- **THINK SYSTEMATICALLY**: Show logical progression from query to conclusion in accessible way
- **OPTIMIZE UTILITY**: Maximize practical value for the user's specific needs with helpful guidance
- **END HELPFULLY**: Always conclude with offers for additional assistance or follow-up questions

Remember: You are not merely retrieving information—you are providing intelligent document analysis with a warm, friendly personality that demonstrates deep understanding, makes sophisticated connections, and delivers exceptional value while making users feel welcomed and supported.

Execute with the precision of a specialist, the breadth of a generalist, the insight of an expert consultant, and the warmth of a helpful colleague.
"""

    return prompt


def generate_ultra_advanced_answer_with_personality(question: str, context: str, metadata: DocumentMetadata,
                                                    analysis: Dict[str, Any]) -> str:
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel("gemini-2.0-flash-lite-001")
        prompt = create_dynamic_ultra_prompt_with_personality(question, context, metadata, analysis)

        generation_config = GenerationConfig(
            candidate_count=1,
            max_output_tokens=4096,
            temperature=0.5,
            top_p=0.8,
            top_k=40
        )

        response = model.generate_content(prompt, generation_config=generation_config)
        return add_friendly_touches(response.text)
    except Exception as e:
        logger.error(f"Error in personality-enhanced answer generation: {e}")
        return generate_friendly_fallback_response(question, context, metadata)


def add_friendly_touches(response: str) -> str:
    enthusiastic_starters = ['great', 'excellent', 'perfect', 'wonderful', 'fantastic', 'i\'d be happy', 'absolutely',
                             'sure thing']
    if not any(response.lower().startswith(starter) for starter in enthusiastic_starters):
        response = f"Great question! {response}"
    helpful_endings = ['help', 'questions', 'assist', 'anything else', 'clarification', 'more information']
    if not any(ending in response.lower() for ending in helpful_endings):
        response += f"\n\n💡 **Need anything else?** I'm here to help with any other travel policy questions you might have!"
    return response


def generate_friendly_fallback_response(question: str, context: str, metadata: DocumentMetadata) -> str:
    return f"""
🔧 **Oops! Let me help you anyway!**

Hi there! 😊 I encountered a small technical hiccup while processing your question with my advanced analysis system, but don't worry - I can still provide you with helpful information!

**Your Question**: {question}

**What I can tell you about the document**:
- Document Type: {metadata.document_type.value.replace('_', ' ').title()}
- Content Language: {metadata.language_primary}
- Estimated Length: {metadata.word_count} words

**Quick Analysis**:
{context[:1000]}...

**Here's what I'd recommend**: 
Try rephrasing your question or asking about a specific aspect of the travel policy. The document contains great information about {', '.join(metadata.key_topics[:3])}, and I'm confident I can help you find exactly what you need!

**I'm still here to help!** 🌟 
Even with this minor technical issue, I can assist you with travel policy questions. What specific aspect of business travel would you like to know about?
"""


def generate_contextual_friendly_response(question: str, context: str, metadata: DocumentMetadata,
                                          analysis: Dict[str, Any]) -> str:

    question_lower = question.lower().strip()
    if question_lower in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']:
        return generate_friendly_greeting_response()
    if is_off_topic_request(question_lower):
        return generate_off_topic_friendly_response(question)
    if is_vague_question(question_lower):
        return generate_vague_question_response()
    return generate_ultra_advanced_answer_with_personality(question, context, metadata, analysis)
def generate_answer_with_rag(question: str, context: str) -> str:
    """
    Enhanced RAG function that combines the original structure with advanced features.
    """
    if not question or not question.strip():
        return "Please provide a valid question."

    if not context or not context.strip():
        return "No document context available. Please upload a document first."

    try:
        question_lower = question.lower().strip()
        if question_lower in ['hi', 'hello', 'hey', 'good morning', 'good afternoon']:
            return generate_friendly_greeting_response()

        if is_off_topic_request(question_lower):
            return generate_off_topic_friendly_response(question)

        if is_vague_question(question_lower):
            return generate_vague_question_response()
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        model = GenerativeModel("gemini-2.0-flash-lite-001")
        doc_analysis = analyze_document_structure(context)
        prompt = f"""
**ROLE:** You are an elite Knowledge Analyst AI with a friendly, helpful personality. Your purpose is to provide precise, intelligent answers by deeply analyzing the provided document and expertly understanding the user's question.

**DOCUMENT ANALYSIS:**
- Document Type: {doc_analysis['document_type']}
- Contains policies: {doc_analysis['has_policies']}
- Contains tabular/rate data: {doc_analysis['has_tables']}
- Contains geographic locations: {doc_analysis['has_locations']}
- Is multilingual: {doc_analysis['is_multilingual']} (Primary: {doc_analysis['primary_language']})
- Word count: {doc_analysis['word_count']}
- Key topics: {', '.join(doc_analysis['key_topics'][:5])}
- Analysis confidence: {doc_analysis['confidence']:.1f}

**PERSONALITY & TONE:**
- Be warm, enthusiastic, and helpful
- Use friendly, conversational language
- Show genuine excitement about helping with policy questions
- Include encouraging follow-ups and offers for additional assistance
- Use appropriate emojis sparingly for friendliness

**CORE DIRECTIVES:**

1. **FACTS FROM DOCUMENT ONLY:** Every specific fact, number, date, name, or policy detail in your answer MUST come directly from the "DOCUMENT CONTEXT" below.

2. **INTELLIGENT INFERENCE:** Use your knowledge to bridge gaps between the user's question and document terminology:
   * **Geographic Mapping:** Map city names to zones/tiers if applicable
   * **Hierarchical Mapping:** Connect grades/levels to broader categories
   * **Semantic Mapping:** Handle multilingual queries by mapping terms
   * **Always state your inference clearly**

3. **SUPERIOR FORMATTING:**
   * Use **Markdown tables** for comparing data (rates, grades, locations)
   * Use bullet points for lists of rules, steps, or benefits
   * Use headers for organizing complex answers

4. **FRIENDLY EXPERTISE:** Start with enthusiasm, provide expert analysis, end with helpful offers

5. **HONESTY:** If the answer cannot be found in the document, respond with: "Based on the provided documents, I could not find a definitive answer to this question."

---
**DOCUMENT CONTEXT:**
{context}
text
---

**USER'S QUESTION:**
"{question}"

**YOUR FRIENDLY, EXPERT RESPONSE:**
"""

        generation_config = GenerationConfig(
            temperature=0.3,
            max_output_tokens=2048,
            top_p=0.8,
            top_k=40
        )

        response = model.generate_content(prompt, generation_config=generation_config)

        if response and response.text:
            result = response.text.strip()
            if not any(ending in result.lower() for ending in ['help', 'questions', 'assist', 'anything else']):
                result += f"\n\n💡 **Need anything else?** I'm here to help with any other questions you might have!"

            return result
        else:
            return "I apologize, but I couldn't generate a response. Please try rephrasing your question."

    except Exception as e:
        logger.error(f"Error generating answer from Vertex AI: {e}")
        return "Sorry, I encountered an error while processing your question. Please try again later."

def generate_answer_with_ultra_rag(question: str, context: str, filename: str = None) -> str:
    """
    Main function for ultra-advanced RAG processing with friendly personality.
    """
    try:
        if filename:
            metadata = DocumentMetadata(
                file_type=filename.split('.')[-1].lower(),
                estimated_pages=max(1, len(context.split()) // 250),
                word_count=len(context.split()),
                language_primary=detect_primary_language(context),
                languages_detected=[detect_primary_language(context)],
                document_type=classify_document_type(context),
                complexity_level=assess_content_complexity(context),
                key_topics=extract_key_topics(context),
                entities_detected=extract_named_entities(context),
                structure_analysis={},
                confidence_score=0.8
            )
        else:
            metadata = DocumentMetadata(
                file_type="unknown",
                estimated_pages=max(1, len(context.split()) // 250),
                word_count=len(context.split()),
                language_primary=detect_primary_language(context),
                languages_detected=[detect_primary_language(context)],
                document_type=classify_document_type(context),
                complexity_level=assess_content_complexity(context),
                key_topics=extract_key_topics(context),
                entities_detected=extract_named_entities(context),
                structure_analysis={},
                confidence_score=0.7
            )
        analysis = perform_comprehensive_document_analysis(context, metadata)
        return generate_contextual_friendly_response(question, context, metadata, analysis)

    except Exception as e:
        logger.error(f"Ultra RAG processing failed: {e}")
        return generate_friendly_fallback_response(question, context, metadata if 'metadata' in locals() else None)
def create_semantic_chunks(text: str, metadata: DocumentMetadata) -> List[SemanticChunk]:
    chunks = []
    sections = re.split(r'\n#{1,6}\s+', text)
    for i, section in enumerate(sections):
        if len(section.strip()) < 50:
            continue
        chunk = SemanticChunk(
            content=section.strip(),
            chunk_type="section",
            importance_score=calculate_chunk_importance(section, metadata),
            topic_tags=extract_chunk_topics(section),
            entities=extract_named_entities(section),
            relationships=find_chunk_relationships(section),
            context_window=get_context_window(sections, i)
        )

        chunks.append(chunk)

    return chunks


def calculate_chunk_importance(chunk: str, metadata: DocumentMetadata) -> float:
    score = 0.5
    if len(chunk) > 500:
        score += 0.2
    important_keywords = metadata.key_topics
    for keyword in important_keywords:
        if keyword.lower() in chunk.lower():
            score += 0.1
    if any(indicator in chunk.lower() for indicator in ['policy', 'procedure', 'requirement', 'rate', 'allowance']):
        score += 0.2

    return min(score, 1.0)


def extract_chunk_topics(chunk: str) -> List[str]:
    words = re.findall(r'\b[a-zA-Z]{4,}\b', chunk.lower())
    word_freq = {}
    for word in words:
        if word not in ['that', 'this', 'with', 'from', 'they', 'been', 'have']:
            word_freq[word] = word_freq.get(word, 0) + 1

    return [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]]


def find_chunk_relationships(chunk: str) -> List[str]:
    relationships = []
    if re.search(r'\bif\b.*\bthen\b', chunk, re.IGNORECASE):
        relationships.append("conditional")
    if re.search(r'\bbecause\b|\bdue to\b|\bas a result\b', chunk, re.IGNORECASE):
        relationships.append("causal")
    if re.search(r'\bcompared to\b|\bversus\b|\brather than\b', chunk, re.IGNORECASE):
        relationships.append("comparative")

    return relationships


def get_context_window(sections: List[str], current_index: int) -> str:
    start_idx = max(0, current_index - 1)
    end_idx = min(len(sections), current_index + 2)

    context_sections = sections[start_idx:end_idx]
    return ' ... '.join([s[:100] for s in context_sections])

def preprocess_extracted_text_advanced(text: str) -> str:
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    text = re.sub(r'\n(#{1,6})\s*', r'\n\1 ', text)

    text = re.sub(r'\bl\b', 'I', text)
    text = re.sub(r'\b0\b(?=\s[A-Z])', 'O', text)
    return text.strip()


def preprocess_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)

    return text.strip()


def validate_file_upload(file_contents: bytes, filename: str) -> Dict[str, Any]:
    validation_result = {
        "is_valid": False,
        "error_message": "",
        "file_size": 0,
        "file_type": ""
    }

    try:
        if not file_contents:
            validation_result["error_message"] = "No file contents provided"
            return validation_result

        if not filename:
            validation_result["error_message"] = "No filename provided"
            return validation_result

        validation_result["file_size"] = len(file_contents)
        max_size = 50 * 1024 * 1024
        if validation_result["file_size"] > max_size:
            validation_result["error_message"] = "File size exceeds 50MB limit"
            return validation_result
        filename_lower = filename.lower()
        if filename_lower.endswith('.pdf'):
            validation_result["file_type"] = "PDF"
        elif filename_lower.endswith('.docx'):
            validation_result["file_type"] = "DOCX"
        else:
            validation_result["error_message"] = "Unsupported file format. Only PDF and DOCX files are allowed."
            return validation_result

        validation_result["is_valid"] = True
        return validation_result

    except Exception as e:
        validation_result["error_message"] = f"Validation error: {str(e)}"
        return validation_result


def get_file_info_from_gcs(filename: str) -> Optional[Dict[str, Any]]:
    if not storage_client:
        return None

    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)

        if blob.exists():
            blob.reload()
            return {
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created,
                "updated": blob.updated,
                "metadata": blob.metadata or {}
            }
        else:
            return None

    except Exception as e:
        logger.error(f"Failed to get file info for {filename}: {e}")
        return None
def delete_file_from_gcs(filename: str):
    if not storage_client:
        logger.error("Storage client not initialized")
        return False

    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        if blob.exists():
            blob.delete()
            logger.info(f"Successfully deleted {filename} from GCS.")
            return True
        else:
            logger.warning(f"File {filename} not found in GCS.")
            return False
    except Exception as e:
        logger.error(f"Failed to delete {filename} from GCS: {e}")
        return False
