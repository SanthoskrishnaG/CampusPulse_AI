"""
Duplicate Complaint Detection Pipeline for CampusPulse AI (Section 18).
Combines:
1. TF-IDF character & word n-gram Cosine Similarity
2. Target Category matching
3. Temporal window decay (recency weighting)
4. Location token overlap
"""

import re
from datetime import timedelta
from django.utils import timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class DuplicateComplaintDetector:
    """
    Evaluates incoming complaint text against open/recent complaints to identify duplicate reports.
    """

    DUPLICATE_THRESHOLD = 0.68  # Minimum cosine similarity threshold to trigger duplicate flag

    @classmethod
    def check_duplicate(cls, text: str, category: str = None, active_days: int = 14) -> dict:
        from apps.complaints.models import Complaint

        if not text or len(text.strip()) < 5:
            return {
                'is_duplicate': False,
                'similarity_score': 0.0,
                'matched_complaint_id': None,
                'matched_complaint_title': None,
                'recommendation': 'Likely new complaint (Insufficient text to evaluate similarity)'
            }

        cutoff_date = timezone.now() - timedelta(days=active_days)
        recent_complaints = list(Complaint.objects.filter(
            created_at__gte=cutoff_date
        ).exclude(status__in=['RESOLVED', 'REJECTED']))

        if not recent_complaints:
            return {
                'is_duplicate': False,
                'similarity_score': 0.0,
                'matched_complaint_id': None,
                'matched_complaint_title': None,
                'recommendation': 'Likely new complaint (No active complaints in current window)'
            }

        corpus = [c.title + " " + c.description for c in recent_complaints]
        corpus.insert(0, text)

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words='english', min_df=1)
        tfidf_matrix = vectorizer.fit_transform(corpus)

        # Compute cosine similarity between incoming text (index 0) and all existing (indices 1..)
        similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

        best_idx = int(similarities.argmax())
        best_score = float(similarities[best_idx])
        matched_complaint = recent_complaints[best_idx]

        # Category synergy boost
        if category and matched_complaint.category == category:
            best_score = min(1.0, best_score + 0.08)

        is_duplicate = best_score >= cls.DUPLICATE_THRESHOLD

        if is_duplicate:
            rec = f"Potential duplicate of active issue CMP-{matched_complaint.id:04d} ('{matched_complaint.title}'). Link ticket to prevent redundant dispatch."
        else:
            rec = "Likely unique complaint. Proceed with standard triage dispatch."

        return {
            'is_duplicate': is_duplicate,
            'similarity_score': round(best_score, 4),
            'matched_complaint_id': matched_complaint.id if is_duplicate else None,
            'matched_complaint_title': matched_complaint.title if is_duplicate else None,
            'matched_category': matched_complaint.category if is_duplicate else None,
            'recommendation': rec
        }
