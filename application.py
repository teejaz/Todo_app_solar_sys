# AWS Elastic Beanstalk expects the Flask app to be named 'application'
from app import app as application

if __name__ == "__main__":
    application.run()