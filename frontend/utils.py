# frontend/utils.py
import streamlit as st
import logging
from PyPDF2 import PdfReader

logger = logging.getLogger(__name__)


def extract_text(file):
    """
    Extract text from uploaded file (PDF or TXT)
    
    Args:
        file: Uploaded file object from Streamlit
        
    Returns:
        Extracted text as string
    """
    if file is None:
        logger.warning("No file provided to extract_text")
        return ""
    
    logger.info(f"Extracting text from file: {file.name}")
    logger.debug(f"File type: {file.type}")
    
    try:
        if file.type == "application/pdf":
            logger.info("Processing PDF file")
            reader = PdfReader(file)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            logger.info(f"✅ Extracted {len(text)} characters from PDF")
            return text
        
        elif file.type == "text/plain":
            logger.info("Processing TXT file")
            text = file.read().decode("utf-8")
            logger.info(f"✅ Extracted {len(text)} characters from TXT")
            return text
        
        else:
            logger.warning(f"Unsupported file type: {file.type}")
            return ""
    
    except Exception as e:
        logger.error(f"❌ Error extracting text: {str(e)}", exc_info=True)
        return ""


def display_chat(chat_history):
    """
    Display chat history in Streamlit
    
    Args:
        chat_history: List of (role, message) tuples
    """
    logger.debug(f"Displaying {len(chat_history)} chat messages")
    
    for role, msg in chat_history:
        with st.chat_message(role):
            st.write(msg)


def log_page_view(page_name: str):
    """Log when a page is viewed"""
    logger.info("=" * 70)
    logger.info(f"📄 Page View: {page_name}")
    logger.info("=" * 70)


def log_user_action(action: str, details: dict = None):
    """Log user actions"""
    logger.info(f"👤 User Action: {action}")
    if details:
        logger.debug(f"Details: {details}")


logger.info("✅ Utils module loaded")