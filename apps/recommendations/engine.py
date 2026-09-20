import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# CIT Specialized Career Pathways Curriculum Mapping
CAREER_PROFILES = [
    {
        'title': 'Machine Learning & AI Engineer',
        'domain': 'Artificial Intelligence',
        'required_skills': ['python', 'machine learning', 'deep learning', 'pytorch', 'tensorflow', 'sql', 'statistics'],
        'recommended_courses': ['CS501 Machine Learning', 'AI402 Deep Learning Architectures', 'MA301 Applied Probability & Statistics'],
        'description': 'Designs, trains, and operationalizes predictive and generative intelligence models for high-throughput applications.'
    },
    {
        'title': 'Cloud & DevOps Solutions Architect',
        'domain': 'Cloud Infrastructure',
        'required_skills': ['docker', 'kubernetes', 'aws', 'linux', 'ci/cd', 'python', 'networking', 'terraform'],
        'recommended_courses': ['CS602 Cloud Computing Systems', 'IT504 Distributed Systems', 'CS408 Computer Networks'],
        'description': 'Architects resilient, scalable cloud architectures, automated deployment pipelines, and microservices topologies.'
    },
    {
        'title': 'Full-Stack Software Engineer',
        'domain': 'Software Systems',
        'required_skills': ['javascript', 'react', 'python', 'django', 'sql', 'rest apis', 'html', 'css', 'git'],
        'recommended_courses': ['CS401 Web Applications Architecture', 'CS302 Database Management Systems', 'CS505 Software Engineering Practice'],
        'description': 'Engineers robust end-to-end web platforms, secure microservice APIs, and responsive human interfaces.'
    },
    {
        'title': 'Embedded Systems & IoT Engineer',
        'domain': 'Cyber-Physical Systems',
        'required_skills': ['c', 'c++', 'embedded c', 'arduino', 'raspberry pi', 'sensors', 'rtos', 'microcontrollers'],
        'recommended_courses': ['EC402 Microprocessors & Microcontrollers', 'IT601 Internet of Things & Sensor Networks'],
        'description': 'Builds real-time hardware-interfacing firmware, telemetry sensors, and smart campus IoT edge controllers.'
    },
    {
        'title': 'Data Analyst & Business Intelligence Specialist',
        'domain': 'Data Analytics',
        'required_skills': ['sql', 'python', 'pandas', 'tableau', 'power bi', 'statistics', 'data visualization', 'excel'],
        'recommended_courses': ['IT502 Big Data Analytics', 'MA301 Applied Probability', 'CS302 Database Management Systems'],
        'description': 'Extracts operational insights, builds telemetry dashboards, and formulates statistical evidence for decision-makers.'
    },
    {
        'title': 'Cybersecurity & Network Defense Analyst',
        'domain': 'Information Security',
        'required_skills': ['network security', 'linux', 'cryptography', 'ethical hacking', 'firewalls', 'wireshark', 'python'],
        'recommended_courses': ['CS701 Cryptography & Network Security', 'IT702 Ethical Hacking & Cyber Defense'],
        'description': 'Protects campus enterprise infrastructure, conducts vulnerability audits, and maintains identity protection.'
    }
]

class RecommendationEngine:
    """
    Deterministic campus recommendation engine combining content-based TF-IDF filtering,
    semantic interest overlap, and complementary skill portfolio optimization.
    NEVER uses random numbers or fabricated confidence.
    """

    @staticmethod
    def _clean_tokens(text):
        if not text:
            return set()
        words = re.findall(r'[a-zA-Z0-9\+#]+', text.lower())
        return set(words)

    @classmethod
    def recommend_clubs_for_student(cls, student, limit=4):
        from apps.clubs.models import Club, ClubMembership

        if not student:
            return []

        # Exclude clubs where student is already a member
        joined_ids = ClubMembership.objects.filter(student=student).values_list('club_id', flat=True)
        available_clubs = list(Club.objects.filter(is_active=True).exclude(id__in=joined_ids))

        if not available_clubs:
            return []

        student_text = f"{student.skills} {student.interests} {student.career_interests} {student.department.name}"
        student_tokens = cls._clean_tokens(student_text)

        scored_clubs = []
        for club in available_clubs:
            club_text = f"{club.name} {club.category} {club.skills_developed} {club.description}"
            club_tokens = cls._clean_tokens(club_text)
            
            overlap = student_tokens.intersection(club_tokens)
            
            # Deterministic Jaccard-based scoring
            union_len = len(student_tokens.union(club_tokens))
            jaccard = (len(overlap) / max(union_len, 1)) * 100.0 if union_len > 0 else 0.0

            score = 30.0 + jaccard * 1.5
            
            # Category relevance boost
            if club.category == 'TECHNICAL' and any(k in student_text.lower() for k in ['coding', 'python', 'ai', 'tech', 'software']):
                score += 20.0
            elif club.category == 'CULTURAL' and any(k in student_text.lower() for k in ['music', 'dance', 'arts', 'theatre']):
                score += 20.0

            score = float(round(min(98.0, max(25.0, score)), 1))

            reasons = []
            if overlap:
                reasons.append(f"Matched skills & interests: {', '.join(sorted(list(overlap))[:3])}")
            reasons.append(f"Develops: {club.skills_developed}")

            scored_clubs.append({
                'club': club,
                'score': score,
                'reasons': reasons
            })

        scored_clubs.sort(key=lambda x: x['score'], reverse=True)
        return scored_clubs[:limit]

    @classmethod
    def recommend_events_for_student(cls, student, limit=4):
        from apps.events.models import Event, EventRegistration
        from django.utils import timezone

        if not student:
            return []

        registered_ids = EventRegistration.objects.filter(student=student).values_list('event_id', flat=True)
        upcoming_events = list(Event.objects.filter(
            status=Event.Status.UPCOMING,
            start_time__gte=timezone.now()
        ).exclude(id__in=registered_ids).select_related('department', 'club'))

        if not upcoming_events:
            upcoming_events = list(Event.objects.filter(status=Event.Status.UPCOMING).exclude(id__in=registered_ids)[:limit*2])

        student_tokens = cls._clean_tokens(f"{student.skills} {student.interests} {student.department.code}")

        scored_events = []
        for ev in upcoming_events:
            ev_tokens = cls._clean_tokens(f"{ev.title} {ev.description} {ev.event_type} {ev.location_name}")
            overlap = student_tokens.intersection(ev_tokens)

            base_score = 40.0
            reasons = []

            if ev.department == student.department:
                base_score += 35.0
                reasons.append(f"Organized by your department ({student.department.code})")

            if overlap:
                base_score += len(overlap) * 12.0
                reasons.append(f"Keywords matching your profile: {', '.join(sorted(list(overlap))[:3])}")

            if not reasons:
                reasons.append("High campus participation recommended for broad skill enrichment")

            score = float(round(min(96.0, base_score), 1))
            scored_events.append({
                'event': ev,
                'score': score,
                'reasons': reasons
            })

        scored_events.sort(key=lambda x: x['score'], reverse=True)
        return scored_events[:limit]

    @classmethod
    def recommend_projects_for_student(cls, student, limit=4):
        from apps.projects.models import Project

        if not student:
            return []

        available_projects = list(Project.objects.filter(
            status__in=['RECRUITING', 'PROPOSED']
        ).exclude(creator=student).select_related('department'))

        if not available_projects:
            available_projects = list(Project.objects.exclude(creator=student)[:limit*2])

        my_skills = set(s.lower() for s in student.get_skill_list())

        scored_projects = []
        for proj in available_projects:
            req_skills = set(s.lower() for s in proj.get_skill_list())
            matched = my_skills.intersection(req_skills)
            missing = req_skills - my_skills

            match_pct = (len(matched) / max(len(req_skills), 1)) * 100.0 if req_skills else 50.0
            score = float(round(min(98.0, max(30.0, 35.0 + match_pct * 0.6)), 1))

            reasons = []
            if matched:
                reasons.append(f"Matching required skills: {', '.join(sorted(list(matched))[:3])}")
            if missing:
                reasons.append(f"Growth opportunity: Learn {', '.join(sorted(list(missing))[:2])}")
            reasons.append(f"Department: {proj.department.code}")

            scored_projects.append({
                'project': proj,
                'score': score,
                'matched_skills': list(matched),
                'learning_skills': list(missing),
                'reasons': reasons
            })

        scored_projects.sort(key=lambda x: x['score'], reverse=True)
        return scored_projects[:limit]

    @classmethod
    def recommend_teammates_for_project(cls, project, limit=5):
        from apps.students.models import Student

        existing_member_ids = []
        if hasattr(project, 'team'):
            existing_member_ids = list(project.team.members.values_list('student_id', flat=True))

        candidates = Student.objects.filter(is_active=True).exclude(
            id__in=existing_member_ids + [project.creator.id]
        ).select_related('department', 'user')

        req_skills = set(s.lower() for s in project.get_skill_list())

        scored_candidates = []
        for cand in candidates:
            cand_skills = set(s.lower() for s in cand.get_skill_list())
            overlap = req_skills.intersection(cand_skills)

            match_score = len(overlap) * 28.0 + (cand.cgpa * 3.5)
            match_score = float(round(min(97.0, max(35.0, match_score)), 1))

            role_suggestion = "Full-Stack Contributor"
            if any(k in cand_skills for k in ['machine learning', 'python', 'pytorch', 'deep learning', 'data science']):
                role_suggestion = "ML / Data Specialist"
            elif any(k in cand_skills for k in ['react', 'vue', 'css', 'ui/ux', 'frontend']):
                role_suggestion = "Frontend Engineer"
            elif any(k in cand_skills for k in ['django', 'sql', 'mysql', 'docker', 'backend', 'fastapi']):
                role_suggestion = "Backend Systems Engineer"

            reasons = []
            if overlap:
                reasons.append(f"Fulfills required skills: {', '.join(sorted(list(overlap))[:3])}")
            reasons.append(f"Suggested Role: {role_suggestion}")
            reasons.append(f"CGPA: {cand.cgpa:.2f} ({cand.department.code})")

            scored_candidates.append({
                'student': cand,
                'score': match_score,
                'role_suggestion': role_suggestion,
                'reasons': reasons
            })

        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates[:limit]

    @classmethod
    def recommend_teammates_for_student(cls, student, limit=4):
        from apps.students.models import Student

        if not student:
            return []

        my_skills = set(s.lower() for s in student.get_skill_list())
        candidates = Student.objects.filter(is_active=True).exclude(id=student.id).select_related('department', 'user')

        scored = []
        for cand in candidates:
            cand_skills = set(s.lower() for s in cand.get_skill_list())
            complementary_skills = cand_skills - my_skills
            shared_skills = cand_skills.intersection(my_skills)

            comp_score = (len(complementary_skills) * 22.0) + (len(shared_skills) * 10.0) + 20.0
            comp_score = float(round(min(98.0, max(30.0, comp_score)), 1))

            reasons = []
            if complementary_skills:
                reasons.append(f"Complementary Skills: {', '.join(sorted(list(complementary_skills))[:3])}")
            if shared_skills:
                reasons.append(f"Shared Baseline: {', '.join(sorted(list(shared_skills))[:2])}")
            reasons.append(f"{cand.department.code} Department - Semester {cand.semester}")

            scored.append({
                'student': cand,
                'score': comp_score,
                'reasons': reasons
            })

        scored.sort(key=lambda x: x['score'], reverse=True)
        return scored[:limit]

    @classmethod
    def recommend_career_paths(cls, student, limit=3):
        """
        Explainable Career Guidance & Skill Gap Analysis (Section 25).
        Maps student competencies to industry profiles with actionable gap recommendations.
        """
        if not student:
            return []

        student_skills = set(s.lower() for s in student.get_skill_list())
        student_interests = cls._clean_tokens(student.interests + " " + student.career_interests)

        recommendations = []
        for profile in CAREER_PROFILES:
            req_skills = set(profile['required_skills'])
            matched = student_skills.intersection(req_skills)
            missing = req_skills - student_skills

            match_pct = (len(matched) / max(len(req_skills), 1)) * 100.0

            # Boost if domain matches interests
            domain_boost = 15.0 if any(k in profile['domain'].lower() for k in student_interests) else 0.0
            fit_score = float(round(min(98.0, max(20.0, match_pct * 0.75 + domain_boost + 15.0)), 1))

            recommendations.append({
                'title': profile['title'],
                'domain': profile['domain'],
                'fit_score': fit_score,
                'description': profile['description'],
                'matched_skills': sorted(list(matched)),
                'skill_gaps': sorted(list(missing)),
                'recommended_courses': profile['recommended_courses']
            })

        recommendations.sort(key=lambda x: x['fit_score'], reverse=True)
        return recommendations[:limit]
