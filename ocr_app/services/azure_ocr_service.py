from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from django.conf import settings


def extract_text_with_azure(file_path: str) -> dict:
    endpoint = settings.AZURE_DOCINTEL_ENDPOINT
    key = settings.AZURE_DOCINTEL_KEY

    if not endpoint or not key:
        raise ValueError("Azure credentials missing")

    client = DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document(
            model_id="prebuilt-read",
            body=f
        )

    result = poller.result()

    lines = []
    word_confidences=[]

    for page in result.pages:

        if page.lines:
            for line in page.lines:
                lines.append(line.content)

        if page.words:
            for word in page.words:
                if word.confidence is not None:
                    word_confidences.append(word.confidence)

    
    if word_confidences:
        average_confidence = sum(word_confidences) / len(word_confidences)
        confidence_score = round(average_confidence * 100)
    else:
        confidence_score = 0

    return {
        "text": "\n".join(lines),
        "raw": result.as_dict(),
        "confidence_score": confidence_score
    }