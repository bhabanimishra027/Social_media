# 🌐 Django Social Media Platform

A fully functional social media web application built using Django. This platform allows users to connect, share posts, interact through likes and comments, and manage their profiles.

---

## 🚀 Features

- 🔐 User Authentication (Login/Register/Logout)
- 👤 User Profiles
- 📝 Create, Edit, and Delete Posts
- ❤️ Like and Unlike Posts
- 💬 Comment on Posts
- 🖼️ Image Upload Support
- 📰 Dynamic Feed System
- 🔍 Search Functionality (if added)
- 📱 Responsive Design

---

## 🛠️ Tech Stack

- **Backend:** Django, Python
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (default) 
- **Version Control:** Git & GitHub

---

## 📁 Project Structure

  BLOG/
  
    core/
      db.sqlite3
      manage.py
      
      media/
      
        posts/
        
          images/
          
        stories/
        
          images/
          
          videos/
          
      blog/
      
        __init__.py
        admin.py
        apps.py
        consumers.py
        forms.py
        models.py
        routing.py
        tests.py
        urls.py
        views.py
        
      core/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
      __init__.py
      __pycache__/
