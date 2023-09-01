# Oxam

# Educational Exam Platform

A web application for conducting and managing exams in an educational setting. Students can take exams, submit answers, and view their scores, while instructors can create exams, review student scores, and manage course content.

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Setting Up .env](#setting-up-env)
- [Usage](#usage)
- [Screenshots](#screenshots)

## Features

- Role-based access control for students and instructors.
- Create and manage exams with various question types.
- Take exams, submit answers, and view scores.
- Instructor dashboard to review student scores and manage courses.

## Getting Started

### Prerequisites

- Python 3.x
- Flask
- SQLAlchemy
- Flask-Login
- python-dotenv
- Other dependencies (check `requirements.txt`)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/aqib-abdullahi.Oxam.git
   
2. Navigate to the project directory:

   ```bash
   cd Oxam
   
3. Create a virtual environment 
   ```
   python3 -m venv venv
   source venv/bin/activate
   
4. Install the required packages
   ```
   pip install -r requirements.txt
   
5. Setting up .env
   
   - Create a .env file in the project root 
   - Add your sensitive configuration data to the '.env' file.
   - The configuration data should be inbetween the quotation marks.
   ```
   DB_HOST=""
   DB_PORT=""
   DB_NAME=""
   DB_USER=""
   DB_PASS=""
   SECRET_KEY = ""

