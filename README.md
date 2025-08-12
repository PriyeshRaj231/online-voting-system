# Online Voting System with Facial Recognition

A secure, full-stack online voting system built with Python Flask, featuring facial recognition technology for voter verification.

## 🚀 Features

### For Voters
- **Secure Registration**: Register with face capture and password
- **Facial Verification**: Two-factor authentication using facial recognition
- **One-Time Voting**: Each voter can only vote once
- **Real-time Results**: View live voting results and statistics

### For Administrators
- **Candidate Management**: Add, edit, and delete candidates
- **Dashboard Analytics**: View voter turnout, vote counts, and statistics
- **Result Monitoring**: Real-time monitoring of election progress

### Security Features
- **Face Recognition**: Uses `face_recognition` library for accurate facial verification
- **Password Hashing**: Secure password storage using Werkzeug
- **Session Management**: Secure session handling
- **Image Quality Check**: Blur detection for better face recognition accuracy

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite3
- **Face Recognition**: `face_recognition` + OpenCV
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Charts**: Chart.js for result visualization
- **Webcam**: HTML5 MediaDevices API

## 📋 Prerequisites

- Python 3.7 or higher
- Webcam-enabled device
- Modern web browser with camera access

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd onlinevoting
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - The system will automatically create the database and default admin account

## 👥 Default Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`

## 📱 Usage Guide

### For Voters

1. **Registration**
   - Click "Register as Voter" on the home page
   - Fill in your details (name, username, password)
   - Capture your face using the webcam
   - Submit registration

2. **Voting Process**
   - Login with your credentials
   - Complete facial verification
   - Select your preferred candidate
   - Confirm and submit your vote

3. **Viewing Results**
   - Access the results page to see live voting statistics
   - View detailed charts and vote distribution

### For Administrators

1. **Admin Login**
   - Use the default admin credentials
   - Access the admin dashboard

2. **Candidate Management**
   - Add new candidates with photos
   - View candidate statistics
   - Delete candidates if needed

3. **Monitoring**
   - View real-time voter turnout
   - Monitor vote counts and percentages
   - Access detailed analytics

## 🗄️ Database Schema

### Users Table
- `id`: Primary key
- `name`: Full name
- `username`: Unique username
- `password_hash`: Hashed password
- `face_encoding`: Stored facial encoding (BLOB)
- `has_voted`: Boolean flag for vote status

### Candidates Table
- `id`: Primary key
- `name`: Candidate name
- `photo_path`: Path to candidate photo

### Votes Table
- `id`: Primary key
- `voter_id`: Foreign key to users
- `candidate_id`: Foreign key to candidates
- `timestamp`: Vote timestamp

### Admins Table
- `id`: Primary key
- `username`: Admin username
- `password_hash`: Hashed admin password

## 🔧 Configuration

### Environment Variables
- `FLASK_SECRET_KEY`: Set a secure secret key for sessions
- `FLASK_ENV`: Set to 'development' for debug mode

### Face Recognition Settings
- **Tolerance**: 0.6 (adjustable in `app.py`)
- **Blur Threshold**: 100 (adjustable in `is_blurry()` function)

## 🛡️ Security Features

1. **Facial Recognition**
   - Uses advanced face encoding algorithms
   - Blur detection for image quality
   - Multiple face detection prevention

2. **Authentication**
   - Secure password hashing
   - Session-based authentication
   - Two-factor authentication (password + face)

3. **Vote Integrity**
   - One vote per user enforcement
   - Database constraints
   - Audit trail with timestamps

## 📊 API Endpoints

- `GET /`: Home page
- `GET/POST /register`: Voter registration
- `GET/POST /login`: Voter login
- `GET/POST /facial-verification`: Face verification
- `GET /vote`: Voting page
- `POST /submit-vote`: Submit vote (AJAX)
- `GET /results`: View results
- `GET/POST /admin-login`: Admin login
- `GET /admin`: Admin dashboard
- `POST /add-candidate`: Add candidate
- `GET /delete-candidate/<id>`: Delete candidate

## 🐛 Troubleshooting

### Common Issues

1. **Camera Access Denied**
   - Ensure browser has camera permissions
   - Check HTTPS requirement for camera access

2. **Face Recognition Errors**
   - Ensure good lighting conditions
   - Check image quality (not blurry)
   - Ensure face is clearly visible

3. **Database Errors**
   - Delete `voting.db` file to reset database
   - Check file permissions

4. **Dependencies Issues**
   - Update pip: `pip install --upgrade pip`
   - Install system dependencies for OpenCV

### System Requirements

- **Windows**: Visual C++ Build Tools
- **Linux**: `sudo apt-get install python3-dev`
- **macOS**: Xcode Command Line Tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- `face_recognition` library by Adam Geitgey
- OpenCV for computer vision capabilities
- Bootstrap for responsive design
- Chart.js for data visualization

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the documentation
3. Create an issue on GitHub

---

**Note**: This system is designed for educational and demonstration purposes. For production use, additional security measures and compliance requirements should be implemented. 