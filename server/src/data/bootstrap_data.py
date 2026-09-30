"""Bootstrap / generator module for LinkedIn Job Postings dataset.

Conforms to the Kaggle LinkedIn Job Postings schema (`postings.csv`).
If a user already has `data/raw/postings.csv`, it is preserved.
Otherwise, generates a high-fidelity 10,000-row dataset with realistic
distributions, realistic noise, and hiring economics.
"""

from __future__ import annotations
import os
import random
import time
import numpy as np
import pandas as pd

RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "postings.csv")

JOB_FAMILIES = [
    {
        "category": "Software Engineering",
        "titles": [
            "Software Engineer", "Senior Backend Developer", "Full Stack Engineer",
            "DevOps Engineer", "Frontend Developer", "Cloud Solutions Architect",
            "Lead Systems Engineer", "Mobile App Engineer (iOS/Android)",
            "Junior Software Developer", "Principal Infrastructure Engineer"
        ],
        "skills": ["Python", "JavaScript", "React", "Node.js", "Docker", "Kubernetes", "AWS", "SQL", "Git", "CI/CD"],
        "base_salary": (95000, 195000),
        "base_cvr": 0.075
    },
    {
        "category": "Data & AI",
        "titles": [
            "Data Scientist", "Machine Learning Engineer", "Data Analyst",
            "Senior BI Analyst", "AI Research Scientist", "Data Engineer",
            "Analytics Engineer", "Quantitative Researcher"
        ],
        "skills": ["Python", "SQL", "Pandas", "Scikit-Learn", "PyTorch", "Tableau", "Spark", "Snowflake", "Statistics"],
        "base_salary": (90000, 185000),
        "base_cvr": 0.082
    },
    {
        "category": "Product & Design",
        "titles": [
            "Product Manager", "Senior Technical Product Manager", "UI/UX Designer",
            "Product Designer", "Associate Product Manager", "Design Systems Lead"
        ],
        "skills": ["Figma", "User Research", "Agile", "Roadmapping", "Wireframing", "A/B Testing", "Data Analysis"],
        "base_salary": (85000, 165000),
        "base_cvr": 0.068
    },
    {
        "category": "Sales & Business Development",
        "titles": [
            "Sales Development Representative", "Account Executive",
            "Senior Enterprise Account Executive", "Sales Manager",
            "Business Development Lead", "Channel Partnerships Manager"
        ],
        "skills": ["CRM", "Salesforce", "Cold Outreach", "B2B Sales", "Negotiation", "Pipeline Management"],
        "base_salary": (60000, 140000),
        "base_cvr": 0.062
    },
    {
        "category": "Marketing & Growth",
        "titles": [
            "Growth Marketing Manager", "Content Strategist", "SEO Specialist",
            "Performance Marketing Lead", "Social Media Coordinator", "Brand Director"
        ],
        "skills": ["Google Ads", "SEO", "Copywriting", "HubSpot", "Meta Ads", "Analytics", "Email Marketing"],
        "base_salary": (58000, 135000),
        "base_cvr": 0.070
    },
    {
        "category": "Operations & HR",
        "titles": [
            "Talent Acquisition Specialist", "HR Business Partner", "Operations Coordinator",
            "Recruiting Manager", "People Operations Lead", "Office Administrator"
        ],
        "skills": ["Workday", "Onboarding", "Sourcing", "HR Compliance", "Employee Relations", "Excel"],
        "base_salary": (52000, 115000),
        "base_cvr": 0.095
    },
    {
        "category": "Customer Support",
        "titles": [
            "Customer Support Representative", "Technical Support Specialist",
            "Customer Success Manager", "Client Onboarding Specialist"
        ],
        "skills": ["Zendesk", "Intercom", "Customer Empathy", "Troubleshooting", "SLA Management"],
        "base_salary": (45000, 90000),
        "base_cvr": 0.110
    }
]

COMPANIES = [
    "Apex Tech Systems", "CloudScale Networks", "Beacon Health Solutions",
    "Nexus Digital Partners", "Starlight Media", "Vanguard Financial Analytics",
    "Horizon Logistics Corp", "Pinnacle Energy Group", "Quantum Leap Robotics",
    "BlueSky Retail Group", "Crestview Capital", "OmniChannel Innovations",
    "AeroDynamic Labs", "Pulse Health Tech", "TerraFirma Agritech",
    "Velocity Mobility", "Hyperion Cyber Security", "Elevate Talent Labs"
]

LOCATIONS = [
    ("San Francisco, CA", "Tier 1", 1.25),
    ("New York, NY", "Tier 1", 1.20),
    ("Seattle, WA", "Tier 1", 1.15),
    ("Austin, TX", "Tier 2", 1.00),
    ("Boston, MA", "Tier 1", 1.12),
    ("Chicago, IL", "Tier 2", 0.98),
    ("Denver, CO", "Tier 2", 0.95),
    ("Atlanta, GA", "Tier 2", 0.92),
    ("Dallas, TX", "Tier 2", 0.92),
    ("Raleigh, NC", "Tier 3", 0.88),
    ("Salt Lake City, UT", "Tier 3", 0.88),
    ("Remote", "Remote", 1.05)
]

EXPERIENCE_LEVELS = [
    ("Internship", 0.50, 1.40),
    ("Entry level", 0.70, 1.30),
    ("Associate", 0.85, 1.15),
    ("Mid-Senior level", 1.15, 0.95),
    ("Director", 1.65, 0.60),
    ("Executive", 2.20, 0.40)
]

WORK_TYPES = ["Full-time", "Part-time", "Contract", "Temporary", "Internship"]

DESCRIPTION_TEMPLATES = [
    """About the Role:
We are looking for an exceptional {title} to join our high-growth team at {company}.
In this position, you will be instrumental in executing our strategic roadmap, collaborating cross-functionally across engineering, product, and leadership.

Key Responsibilities:
- Design, build, and maintain mission-critical projects and systems.
- Partner with team members to deliver scalable, high-impact results.
- Identify performance bottlenecks and implement reliable architectural fixes.
- Champion quality, best practices, and continuous learning.

Qualifications & Requirements:
- Demonstrated experience in relevant roles or practical internships.
- Core proficiency with {skills}.
- Strong communication skills, analytical rigor, and bias for action.
- Ability to work effectively in a modern collaborative environment.

What We Offer:
- Competitive compensation, comprehensive health benefits, and 401(k) matching.
- Flexible work arrangements and generous paid time off.
- Meaningful professional development stipends and mentorship.""",

    """{company} is expanding rapidly and hiring a motivated {title}!
If you are passionate about driving impact, solving difficult problems, and collaborating with a world-class team, we want to hear from you.

What you'll do:
- Drive project execution from inception to release.
- Work closely with stakeholders to refine requirements and metrics.
- Utilize modern toolsets including {skills}.
- Contribute to architectural guidelines and documentation.

Required Experience:
- Background matching the requirements of {title}.
- Practical experience with {skills}.
- Problem-solving orientation and team player mentality.

Benefits:
- Health, dental, vision coverage from day one.
- Equity options and performance bonuses.
- Flexible remote or hybrid options.""",

    """Position: {title}
Location: {location}
Company: {company}

Summary:
As a {title} at {company}, you will take ownership of key operational and technical workstreams.
You will work in a fast-paced environment where your contributions directly shape our customers' success.

Responsibilities:
- Collaborate with leadership to establish milestones.
- Deliver results leveraging {skills}.
- Monitor KPIs and optimize workflows.

Requirements:
- Proven track record in equivalent roles.
- Familiarity with {skills}.
- Proactive attitude and willingness to tackle challenges head-on."""
]


def generate_linkedin_job_postings(num_rows: int = 10000, seed: int = 42) -> pd.DataFrame:
    """Generate a realistic dataset mirroring Kaggle LinkedIn Job Postings schema."""
    random.seed(seed)
    np.random.seed(seed)

    base_time = int(time.time()) - 180 * 86400  # Past 6 months
    rows = []

    for i in range(1, num_rows + 1):
        job_id = 3700000000 + i
        family = random.choice(JOB_FAMILIES)
        title = random.choice(family["titles"])
        company = random.choice(COMPANIES)
        loc_name, loc_tier, loc_mult = random.choice(LOCATIONS)
        exp_level, exp_sal_mult, exp_cvr_mult = random.choices(
            EXPERIENCE_LEVELS, weights=[0.06, 0.22, 0.24, 0.35, 0.10, 0.03]
        )[0]
        work_type = random.choices(WORK_TYPES, weights=[0.75, 0.08, 0.10, 0.04, 0.03])[0]
        remote_allowed = 1 if (loc_name == "Remote" or random.random() < 0.28) else 0

        # Skills list
        selected_skills = random.sample(family["skills"], k=random.randint(3, min(7, len(family["skills"]))))
        skills_str = ", ".join(selected_skills)

        # Salary specification (approx 65% specify salary, 35% omit)
        has_salary = random.random() < 0.65
        pay_period = random.choices(["YEARLY", "HOURLY"], weights=[0.88, 0.12])[0]

        if has_salary:
            min_base, max_base = family["base_salary"]
            mid_sal = (min_base + max_base) / 2.0 * exp_sal_mult * loc_mult * random.uniform(0.90, 1.15)
            spread = random.uniform(0.10, 0.25)
            min_sal_annual = mid_sal * (1.0 - spread)
            max_sal_annual = mid_sal * (1.0 + spread)

            if pay_period == "HOURLY":
                min_salary = round(min_sal_annual / 2080.0, 2)
                max_salary = round(max_sal_annual / 2080.0, 2)
                med_salary = round((min_salary + max_salary) / 2.0, 2)
            else:
                min_salary = round(min_sal_annual / 500.0) * 500
                max_salary = round(max_sal_annual / 500.0) * 500
                med_salary = round((min_salary + max_salary) / 2.0)
            compensation_type = "BASE_SALARY"
            currency = "USD"
        else:
            min_salary = np.nan
            max_salary = np.nan
            med_salary = np.nan
            pay_period = None
            compensation_type = None
            currency = None

        # Description text
        tmpl = random.choice(DESCRIPTION_TEMPLATES)
        description = tmpl.format(
            title=title, company=company, location=loc_name, skills=skills_str
        )
        # Randomly expand or trim description length
        if random.random() < 0.25:
            description += "\n\nAdditional Notes:\nPlease submit your portfolio or GitHub profile with your application. Applicants requiring visa sponsorship are welcome to apply."
        elif random.random() < 0.15:
            # Verbose description
            description += "\n\nCorporate Values & Culture:\nWe believe in integrity, customer focus, continuous feedback loops, and agility. Our teams follow two-week sprint cycles with daily standups."

        desc_len = len(description)

        # Timing
        post_offset = random.randint(0, 170 * 86400)
        listed_time = (base_time + post_offset) * 1000  # ms epoch
        original_listed_time = listed_time

        sponsored = 1 if random.random() < 0.32 else 0

        # Traffic & Engagement economics
        # Base views follows lognormal distribution
        base_views = np.random.lognormal(mean=4.2, sigma=0.65)
        if sponsored == 1:
            base_views *= random.uniform(1.6, 2.5)  # Sponsored postings get more views
        views = max(5, int(round(base_views)))

        # Conversion rate (applies / views) driver:
        # Base family CVR * experience multiplier
        cvr = family["base_cvr"] * exp_cvr_mult

        # Realistic recruitment advertising factors:
        # 1. Salary disclosure effect: clear salary increases applicant intent by ~25-35%
        if has_salary:
            cvr *= random.uniform(1.22, 1.38)
        else:
            cvr *= random.uniform(0.75, 0.88)

        # 2. Remote flexibility boost:
        if remote_allowed == 1:
            cvr *= random.uniform(1.20, 1.35)

        # 3. Description length penalty if excessively long or too brief
        if desc_len < 600:
            cvr *= 0.85
        elif desc_len > 2200:
            cvr *= 0.88

        # 4. Sponsored postings tend to get slightly broader/lower-intent viewers
        if sponsored == 1:
            cvr *= random.uniform(0.85, 0.95)

        # 5. Natural noise / unobserved job appeal
        cvr_noise = np.random.normal(loc=1.0, scale=0.18)
        cvr = max(0.005, min(0.35, cvr * cvr_noise))

        # Expected applications with binomial/Poisson sampling
        applies = int(np.random.binomial(n=views, p=min(0.95, cvr)))

        rows.append({
            "job_id": job_id,
            "company_name": company,
            "title": title,
            "description": description,
            "max_salary": max_salary,
            "med_salary": med_salary,
            "min_salary": min_salary,
            "pay_period": pay_period,
            "formatted_work_type": work_type,
            "location": loc_name,
            "applies": applies,
            "original_listed_time": original_listed_time,
            "remote_allowed": remote_allowed,
            "views": views,
            "job_posting_url": f"https://www.linkedin.com/jobs/view/{job_id}",
            "application_url": f"https://www.linkedin.com/jobs/apply/{job_id}",
            "formatted_experience_level": exp_level,
            "skills_desc": skills_str,
            "listed_time": listed_time,
            "sponsored": sponsored,
            "work_type": work_type,
            "currency": currency,
            "compensation_type": compensation_type
        })

    df = pd.DataFrame(rows)
    return df


def ensure_dataset(dest_path: str = RAW_DATA_PATH, num_rows: int = 10000) -> str:
    """Ensure raw dataset exists. If missing, generate it."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1024:
        print(f"[Dataset] Using existing raw dataset at: {dest_path}")
        return dest_path

    print(f"[Dataset] Raw dataset not found at {dest_path}. Generating {num_rows} realistic postings...")
    df = generate_linkedin_job_postings(num_rows=num_rows)
    df.to_csv(dest_path, index=False)
    print(f"[Dataset] Successfully generated and saved dataset ({len(df)} rows) to: {dest_path}")
    return dest_path


if __name__ == "__main__":
    ensure_dataset()
