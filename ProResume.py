import streamlit as st
import pandas as pd
import base64,random
import time,datetime
#libraries to parse the resume pdf files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
import os
os.environ["PAFY_BACKEND"] = "internal"
import pafy
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import pafy #for uploading youtube videos
import PyPDF2
from fpdf import FPDF
import plotly.express as px #to create visualisations at the admin session
import nltk
nltk.download('stopwords')
import pdfkit
import requests
# Function to generate the resume
def generate_resume(data):
    # Define your Hugging Face API endpoint and headers
    api_url = "https://api-inference.huggingface.co/models/gpt2"
    headers = {
        "Authorization": f"Bearer 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"}

    # Craft the prompt
    prompt = f"Craft a well-structured resume with the following details:\n\n{data}"

    # Make a request to the API
    response = requests.post(api_url, headers=headers, json={"inputs": prompt})

    if response.status_code == 200:
        return response.text  # Return the generated resume text
    else:
        st.error("Error generating resume. Please try again.")


# Set up the website title and layout
st.set_page_config(page_title="ProResume", layout="centered")

def get_table_download_link(df,filename,text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

#CONNECT TO DATABASE

connection = pymysql.connect(host='localhost',user='root',password='1234',db='cv')
cursor = connection.cursor()

def insert_data(name,email,res_score,timestamp,reco_field,skills,recommended_skills,courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (name, email, str(res_score), timestamp, reco_field, skills,recommended_skills,courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

def run():
    st.sidebar.markdown("# Choose User")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(500) NOT NULL,
                     Email_ID VARCHAR(500) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Predicted_Field BLOB NOT NULL,
                     Actual_skills BLOB NOT NULL,
                     Recommended_skills BLOB NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    if choice == 'User':
        # Add the main title
        st.markdown("<h1 style='text-align: center; color: white;'>ProResume</h1>", unsafe_allow_html=True)

        # Add the subtitle and description
        st.markdown(
            "<h2 style='text-align: center; color: white;'>Build Resumes That Shine!</h2>",
            unsafe_allow_html=True,
        )

        # Add the "Get Started" button centered in a column
        col1, col2, col3 = st.columns([2, 2, 1])  # Create three columns with ratios

        # Add the three features section
        st.markdown("<hr>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        # Feature 1: AI-Powered Resume Optimization
        with col1:
            st.image("https://img.icons8.com/clouds/100/000000/brain.png")  # Example icon from icons8
            st.markdown("<h4 style='text-align: center; color: white;'>AI-Powered Resume Generation</h4>", unsafe_allow_html=True)

        # Feature 2: Skills Recommendation
        with col2:
            # Replace with the local image path
            image = Image.open("./Logo/cl.png")
            image = image.resize((130, 100))  # Specify new size
            st.image(image)
            st.markdown("<h4 style='text-align: center; color: white;'>Generate personalised cover letter</h4>", unsafe_allow_html=True)
            

        # Feature 3: Resume Analysis
        with col3:
            st.image("https://img.icons8.com/clouds/100/000000/document.png")  # Example icon from icons8
            st.markdown("<h4 style='text-align: center; color: white;'>Resume Analyzer</h4>", unsafe_allow_html=True)

        # Add background color and style
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #000000;
            }
            h1, h2, h3, p {
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('''<h5 style='text-align: left; color: #f9e79f;'> Upload your resume, and get pro recommendations</h5>''',
                    unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Uploading your Resume...'):
                time.sleep(4)
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            print(resume_data)
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)

                st.header("**Resume Analysis**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Your Basic info**")

                # Collect user input
                name = str(resume_data.get('name', 'N/A') or 'N/A')
                email = str(resume_data.get('email', 'N/A') or 'N/A')
                mobile_number = str(resume_data.get('mobile_number', 'N/A') or 'N/A')
                skills = resume_data.get('skills', [])
                objective = str(resume_data.get('objective', 'N/A'))
                education = str(resume_data.get('education', 'N/A'))
                experience = str(resume_data.get('experience', 'N/A'))
                # Check for missing fields and ask for user input
                if name == 'N/A':
                    name = st.text_input('Please enter your name:')
                else:
                    st.write('Name: ' + name)

                if email == 'N/A':
                    email = st.text_input('Please enter your email:')
                else:
                    st.write('Email: ' + email)

                if mobile_number == 'N/A':
                    mobile_number = st.text_input('Please enter your mobile number:')
                else:
                    st.write('Contact: ' + mobile_number)
                # st.subheader("**Skills Recommendation💡**")
                ## Skill shows

                keywords = st_tags(label='### Your Current Skills',
                text='See our skills recommendation below',
                    value=resume_data['skills'],key = '1  ')

                ##  keywords
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                               'javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                ## Courses recommendation
                for i in resume_data['skills']:
                    ## Data science recommendation
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success(" Our analysis says you are looking for Data Science Jobs.")
                        recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '2')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break

                    ## Web development recommendation
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success(" Our analysis says you are looking for Web Development Jobs ")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '3')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(web_course)
                        break

                    ## Android App Development
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success(" Our analysis says you are looking for Android App Development Jobs ")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '4')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    ## IOS App Development
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success(" Our analysis says you are looking for IOS App Development Jobs ")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '5')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                    ## Ui-UX Recommendation
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success(" Our analysis says you are looking for UI-UX Development Jobs ")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keywords = st_tags(label='### Recommended skills for you.',
                        text='Recommended skills generated from System',value=recommended_skills,key = '6')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break

                
                ## Insert into table
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)

                ### Resume writing recommendation
                st.subheader("Resume Tips & Ideas💡")
                resume_score = 0
                if 'Objective'or 'Summary' in resume_text:
                    resume_score = resume_score+20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #f9e79f;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

                if 'Declaration'  in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Delcaration/h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #f9e79f;'>[-] Please add Declaration. It will give the assurance that everything written on your resume is true and fully acknowledged by you</h4>''',unsafe_allow_html=True)

                if 'Hobbies' or 'Interests'in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #f9e79f;'>[-] Please add Hobbies. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

                if 'Experience' or 'Internships' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Experience </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #f9e79f;'>[-] Please add Experience. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                if 'Projects' or 'Research' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h5 style='text-align: left; color: #f9e79f;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

                st.subheader("**Resume Score📝**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('Your Resume Writing Score: ' + str(score)+'')
                st.warning("Note: This score is calculated based on the content that you have in your Resume. ")

                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                              reco_field, str(resume_data['skills']),str(recommended_skills), str(rec_course))

                if objective == 'N/A':
                    objective = st.text_input('Please enter your objective:')
                if education == 'N/A':
                    education = st.text_input('Please enter your education:')
                if experience == 'N/A':
                    experience = st.text_area('Please describe your experience:', value='', placeholder='Enter your work experience here...')

                # Additional inputs
                job_title = st.text_input("Enter Job Title")
                additional_info = st.text_area("Any Additional Information")

                # Button to generate resume
                if st.button("Generate Resume"):
                    # Prepare the data for the API
                    resume_data = {
                        "Name": name,
                        "Email": email,
                        "Mobile Number": mobile_number,
                        "Skills": ', '.join(skills),
                        "Objective": objective,
                        "Education": education,
                        "Experience": experience,
                        "Job Title": job_title,
                        "Additional Info": additional_info
                    }

                    # Generate the resume
                    generated_resume = generate_resume(resume_data)

                    if generated_resume:
                        # Convert the generated resume to PDF
                        pdfkit.from_string(generated_resume, 'resume.pdf')
                        st.success("Resume generated successfully! Click the button below to download.")

                        # Download link for the PDF
                        with open("resume.pdf", "rb") as f:
                            st.download_button("Download Resume", f, "resume.pdf")

            else:
                st.error('Something went wrong..')
    else:
        ## Admin Side
        st.success('Welcome to Admin Side')
        # st.sidebar.subheader('**ID / Password Required!**')

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'Admin' and ad_password == '1234':
                st.success("Welcome Admin !")
                # Display Data
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("User's Data")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp',
                                                 'Predicted Field', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)
                ## Admin Side Data
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection)

                ## Pie chart for predicted field recommendations
                labels = plot_data.Predicted_Field.unique()
                print(labels)
                values = plot_data.Predicted_Field.value_counts()
                print(values)
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills')
                st.plotly_chart(fig)

            else:
                st.error("Wrong ID & Password Provided")
run()