import re
from flask import Flask, request, render_template
import pickle
import pdfplumber
import docx
from transformers import pipeline
import spacy
from spacy.matcher import Matcher

app = Flask(__name__)

# Load models
rf_classifier_categorization = pickle.load(open('rf_classifier_categorization.pkl', 'rb'))
tfidf_vectorizer_categorization = pickle.load(open('tfidf_vectorizer_categorization.pkl', 'rb'))
rf_classifier_job_recommendation = pickle.load(open('rf_classifier_job_recommendation.pkl', 'rb'))
tfidf_vectorizer_job_recommendation = pickle.load(open('tfidf_vectorizer_job_recommendation.pkl', 'rb'))

# Load BERT NER model
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", tokenizer="dslim/bert-base-NER")

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Define keyword lists for skills and education
skill_keywords = ['Python', 'Data Analysis', 'Machine Learning', 'Communication', 'Project Management', 'Deep Learning', 'SQL',
        'Tableau',
        'Java', 'C++', 'JavaScript', 'HTML', 'CSS', 'React', 'Angular', 'Node.js', 'MongoDB', 'Express.js', 'Git',
        'Research', 'Statistics', 'Quantitative Analysis', 'Qualitative Analysis', 'SPSS',  'Data Visualization',
        'Matplotlib',
        'Seaborn', 'Plotly', 'Pandas', 'Numpy', 'Scikit-learn', 'TensorFlow', 'Keras', 'PyTorch', 'NLTK', 'Text Mining',
        'Natural Language Processing', 'Computer Vision', 'Image Processing', 'OCR', 'Speech Recognition',
        'Recommendation Systems',
        'Collaborative Filtering', 'Content-Based Filtering', 'Reinforcement Learning', 'Neural Networks',
        'Convolutional Neural Networks',
        'Recurrent Neural Networks', 'Generative Adversarial Networks', 'XGBoost', 'Random Forest', 'Decision Trees',
        'Support Vector Machines',
        'Linear Regression', 'Logistic Regression', 'K-Means Clustering', 'Hierarchical Clustering', 'DBSCAN',
        'Association Rule Learning',
        'Apache Hadoop', 'Apache Spark', 'MapReduce', 'Hive', 'HBase', 'Apache Kafka', 'Data Warehousing', 'ETL',
        'Big Data Analytics',
        'Cloud Computing', 'Amazon Web Services (AWS)', 'Microsoft Azure', 'Google Cloud Platform (GCP)', 'Docker',
        'Kubernetes', 'Linux',
        'Shell Scripting', 'Cybersecurity', 'Network Security', 'Penetration Testing', 'Firewalls', 'Encryption',
        'Malware Analysis',
        'Digital Forensics', 'CI/CD', 'DevOps', 'Agile Methodology', 'Scrum', 'Kanban', 'Continuous Integration',
        'Continuous Deployment',
        'Software Development', 'Web Development', 'Mobile Development', 'Backend Development', 'Frontend Development',
        'Full-Stack Development',
        'UI/UX Design', 'Responsive Design', 'Wireframing', 'Prototyping', 'User Testing', 'Adobe Creative Suite',
        'Photoshop', 'Illustrator',
        'InDesign', 'Figma', 'Sketch', 'Zeplin', 'InVision', 'Product Management', 'Market Research',
        'Customer Development', 'Lean Startup',
        'Business Development', 'Sales', 'Marketing', 'Content Marketing', 'Social Media Marketing', 'Email Marketing',
        'SEO', 'SEM', 'PPC',
        'Google Analytics', 'Facebook Ads', 'LinkedIn Ads', 'Lead Generation', 'Customer Relationship Management (CRM)',
        'Salesforce',
        'HubSpot', 'Zendesk', 'Intercom', 'Customer Support', 'Technical Support', 'Troubleshooting',
        'Ticketing Systems', 'ServiceNow',
        'ITIL', 'Quality Assurance', 'Manual Testing', 'Automated Testing', 'Selenium', 'JUnit', 'Load Testing',
        'Performance Testing',
        'Regression Testing', 'Black Box Testing', 'White Box Testing', 'API Testing', 'Mobile Testing',
        'Usability Testing', 'Accessibility Testing',
        'Cross-Browser Testing', 'Agile Testing', 'User Acceptance Testing', 'Software Documentation',
        'Technical Writing', 'Copywriting',
        'Editing', 'Proofreading', 'Content Management Systems (CMS)', 'WordPress', 'Joomla', 'Drupal', 'Magento',
        'Shopify', 'E-commerce',
        'Payment Gateways', 'Inventory Management', 'Supply Chain Management', 'Logistics', 'Procurement',
        'ERP Systems', 'SAP', 'Oracle',
        'Microsoft Dynamics', 'Tableau', 'Power BI', 'QlikView', 'Looker', 'Data Warehousing', 'ETL',
        'Data Engineering', 'Data Governance',
        'Data Quality', 'Master Data Management', 'Predictive Analytics', 'Prescriptive Analytics',
        'Descriptive Analytics', 'Business Intelligence',
        'Dashboarding', 'Reporting', 'Data Mining', 'Web Scraping', 'API Integration', 'RESTful APIs', 'GraphQL',
        'SOAP', 'Microservices',
        'Serverless Architecture', 'Lambda Functions', 'Event-Driven Architecture', 'Message Queues', 'GraphQL',
        'Socket.io', 'WebSockets'
                     'Ruby', 'Ruby on Rails', 'PHP', 'Symfony', 'Laravel', 'CakePHP', 'Zend Framework', 'ASP.NET', 'C#',
        'VB.NET', 'ASP.NET MVC', 'Entity Framework',
        'Spring', 'Hibernate', 'Struts', 'Kotlin', 'Swift', 'Objective-C', 'iOS Development', 'Android Development',
        'Flutter', 'React Native', 'Ionic',
        'Mobile UI/UX Design', 'Material Design', 'SwiftUI', 'RxJava', 'RxSwift', 'Django', 'Flask', 'FastAPI',
        'Falcon', 'Tornado', 'WebSockets',
        'GraphQL', 'RESTful Web Services', 'SOAP', 'Microservices Architecture', 'Serverless Computing', 'AWS Lambda',
        'Google Cloud Functions',
        'Azure Functions', 'Server Administration', 'System Administration', 'Network Administration',
        'Database Administration', 'MySQL', 'PostgreSQL',
        'SQLite', 'Microsoft SQL Server', 'Oracle Database', 'NoSQL', 'MongoDB', 'Cassandra', 'Redis', 'Elasticsearch',
        'Firebase', 'Google Analytics',
        'Google Tag Manager', 'Adobe Analytics', 'Marketing Automation', 'Customer Data Platforms', 'Segment',
        'Salesforce Marketing Cloud', 'HubSpot CRM',
        'Zapier', 'IFTTT', 'Workflow Automation', 'Robotic Process Automation (RPA)', 'UI Automation',
        'Natural Language Generation (NLG)',
        'Virtual Reality (VR)', 'Augmented Reality (AR)', 'Mixed Reality (MR)', 'Unity', 'Unreal Engine', '3D Modeling',
        'Animation', 'Motion Graphics',
        'Game Design', 'Game Development', 'Level Design', 'Unity3D', 'Unreal Engine 4', 'Blender', 'Maya',
        'Adobe After Effects', 'Adobe Premiere Pro',
        'Final Cut Pro', 'Video Editing', 'Audio Editing', 'Sound Design', 'Music Production', 'Digital Marketing',
        'Content Strategy', 'Conversion Rate Optimization (CRO)',
        'A/B Testing', 'Customer Experience (CX)', 'User Experience (UX)', 'User Interface (UI)', 'Persona Development',
        'User Journey Mapping', 'Information Architecture (IA)',
        'Wireframing', 'Prototyping', 'Usability Testing', 'Accessibility Compliance', 'Internationalization (I18n)',
        'Localization (L10n)', 'Voice User Interface (VUI)',
        'Chatbots', 'Natural Language Understanding (NLU)', 'Speech Synthesis', 'Emotion Detection',
        'Sentiment Analysis', 'Image Recognition', 'Object Detection',
        'Facial Recognition', 'Gesture Recognition', 'Document Recognition', 'Fraud Detection',
        'Cyber Threat Intelligence', 'Security Information and Event Management (SIEM)',
        'Vulnerability Assessment', 'Incident Response', 'Forensic Analysis', 'Security Operations Center (SOC)',
        'Identity and Access Management (IAM)', 'Single Sign-On (SSO)',
        'Multi-Factor Authentication (MFA)', 'Blockchain', 'Cryptocurrency', 'Decentralized Finance (DeFi)',
        'Smart Contracts', 'Web3', 'Non-Fungible Tokens (NFTs)']

education_keywords = ['Computer Science', 'Information Technology', 'Software Engineering', 'Electrical Engineering', 'Mechanical Engineering', 'Civil Engineering',
        'Chemical Engineering','Data Scientist', 'Biomedical Engineering', 'Aerospace Engineering', 'Nuclear Engineering', 'Industrial Engineering', 'Systems Engineering',
        'Environmental Engineering', 'Petroleum Engineering', 'Geological Engineering', 'Marine Engineering', 'Robotics Engineering', 'Biotechnology',
        'Biochemistry', 'Microbiology', 'Genetics', 'Molecular Biology', 'Bioinformatics', 'Neuroscience', 'Biophysics', 'Biostatistics', 'Pharmacology',
        'Physiology', 'Anatomy', 'Pathology', 'Immunology', 'Epidemiology', 'Public Health', 'Health Administration', 'Nursing', 'Medicine', 'Dentistry',
        'Pharmacy', 'Veterinary Medicine', 'Medical Technology', 'Radiography', 'Physical Therapy', 'Occupational Therapy', 'Speech Therapy', 'Nutrition',
        'Sports Science', 'Kinesiology', 'Exercise Physiology', 'Sports Medicine', 'Rehabilitation Science', 'Psychology', 'Counseling', 'Social Work',
        'Sociology', 'Anthropology', 'Criminal Justice', 'Political Science', 'International Relations', 'Economics', 'Finance', 'Accounting', 'Business Administration',
        'Management', 'Marketing', 'Entrepreneurship', 'Hospitality Management', 'Tourism Management', 'Supply Chain Management', 'Logistics Management',
        'Operations Management', 'Human Resource Management', 'Organizational Behavior', 'Project Management', 'Quality Management', 'Risk Management',
        'Strategic Management', 'Public Administration', 'Urban Planning', 'Architecture', 'Interior Design', 'Landscape Architecture', 'Fine Arts',
        'Visual Arts', 'Graphic Design', 'Fashion Design', 'Industrial Design', 'Product Design', 'Animation', 'Film Studies', 'Media Studies',
        'Communication Studies', 'Journalism', 'Broadcasting', 'Creative Writing', 'English Literature', 'Linguistics', 'Translation Studies',
        'Foreign Languages', 'Modern Languages', 'Classical Studies', 'History', 'Archaeology', 'Philosophy', 'Theology', 'Religious Studies',
        'Ethics', 'Education', 'Early Childhood Education', 'Elementary Education', 'Secondary Education', 'Special Education', 'Higher Education',
        'Adult Education', 'Distance Education', 'Online Education', 'Instructional Design', 'Curriculum Development'
        'Library Science', 'Information Science', 'Computer Engineering', 'Software Development', 'Cybersecurity', 'Information Security',
        'Network Engineering', 'Data Science', 'Data Analytics', 'Business Analytics', 'Operations Research', 'Decision Sciences',
        'Human-Computer Interaction', 'User Experience Design', 'User Interface Design', 'Digital Marketing', 'Content Strategy',
        'Brand Management', 'Public Relations', 'Corporate Communications', 'Media Production', 'Digital Media', 'Web Development',
        'Mobile App Development', 'Game Development', 'Virtual Reality', 'Augmented Reality', 'Blockchain Technology', 'Cryptocurrency',
        'Digital Forensics', 'Forensic Science', 'Criminalistics', 'Crime Scene Investigation', 'Emergency Management', 'Fire Science',
        'Environmental Science', 'Climate Science', 'Meteorology', 'Geography', 'Geomatics', 'Remote Sensing', 'Geoinformatics',
        'Cartography', 'GIS (Geographic Information Systems)', 'Environmental Management', 'Sustainability Studies', 'Renewable Energy',
        'Green Technology', 'Ecology', 'Conservation Biology', 'Wildlife Biology', 'Zoology']

def cleanResume(txt):
    cleanText = re.sub('http\S+\s', ' ', txt)
    cleanText = re.sub('RT|cc', ' ', cleanText)
    cleanText = re.sub('#\S+\s', ' ', cleanText)
    cleanText = re.sub('@\S+', '  ', cleanText)
    cleanText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', cleanText)
    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)
    cleanText = re.sub('\s+', ' ', cleanText)
    return cleanText

def pdf_to_text(file):
    text = ''
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

def docx_to_text(file):
    doc = docx.Document(file)
    text = '\n'.join([para.text for para in doc.paragraphs])
    return text

def txt_to_text(file):
    return file.read().decode('utf-8')

def extract_contact_number_from_resume(text):
    pattern = r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
    match = re.search(pattern, text)
    return match.group() if match else None

def extract_email_from_resume(text):
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    match = re.search(pattern, text)
    return match.group() if match else None

def extract_name(resume_text):
    matcher = Matcher(nlp.vocab)
    patterns = [
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}],
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}],
        [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS': 'PROPN'}]
    ]
    for pattern in patterns:
        matcher.add('NAME', patterns=[pattern])
    doc = nlp(resume_text)
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        return span.text
    return None

def extract_information_from_resume(text):
    name = extract_name(text)
    extracted_skills = [skill for skill in skill_keywords if skill.lower() in text.lower()]
    extracted_education = [edu for edu in education_keywords if edu.lower() in text.lower()]
    return name, extracted_skills, extracted_education

def predict_category(resume_text):
    resume_text = cleanResume(resume_text)
    resume_tfidf = tfidf_vectorizer_categorization.transform([resume_text])
    predicted_category = rf_classifier_categorization.predict(resume_tfidf)[0]
    return predicted_category

def job_recommendation(resume_text):
    resume_text = cleanResume(resume_text)
    resume_tfidf = tfidf_vectorizer_job_recommendation.transform([resume_text])
    recommended_job = rf_classifier_job_recommendation.predict(resume_tfidf)[0]
    return recommended_job

@app.route('/')
def resume():
    return render_template("resume.html")

@app.route('/pred', methods=['POST'])
def pred():
    if 'resume' in request.files:
        file = request.files['resume']
        filename = file.filename
        if filename.endswith('.pdf'):
            text = pdf_to_text(file)
        elif filename.endswith('.docx'):
            text = docx_to_text(file)
        elif filename.endswith('.txt'):
            text = txt_to_text(file)
        else:
            return render_template('resume.html', message="Invalid file format. Please upload a PDF, DOCX, or TXT file.")
        predicted_category = predict_category(text)
        recommended_job = job_recommendation(text)
        phone = extract_contact_number_from_resume(text)
        email = extract_email_from_resume(text)
        name, extracted_skills, extracted_education = extract_information_from_resume(text)
        return render_template('resume.html', predicted_category=predicted_category, recommended_job=recommended_job,
                               phone=phone, name=name, email=email, extracted_skills=extracted_skills, extracted_education=extracted_education)
    else:
        return render_template("resume.html", message="No resume file uploaded.")

if __name__ == '__main__':
    app.run(debug=True)
