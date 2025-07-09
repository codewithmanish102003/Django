# BookStore Django Project

A modern, responsive bookstore website built with Django featuring beautiful styling and user-friendly interface.

## Features

### 🎨 Modern Design
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile devices
- **Gradient Headers**: Beautiful gradient backgrounds with smooth animations
- **Card-based Design**: Books and features displayed in attractive cards
- **Hover Effects**: Interactive elements with smooth transitions and animations
- **Professional Typography**: Clean, readable fonts with proper hierarchy

### 📱 Pages
1. **Home Page** (`/`): Welcome page with feature highlights
2. **Book List** (`/books/`): Display all available books in a grid layout
3. **Add Book** (`/add_book`): Form to add new books to the collection
4. **Contact Form** (`/contact/`): User-friendly contact form with validation
5. **Thank You** (`/contact/`): Success page after form submission

### 🎯 Styling Features
- **CSS Grid Layout**: Modern grid system for responsive book display
- **Flexbox Navigation**: Clean, responsive navigation menu
- **Form Styling**: Beautiful form inputs with focus states
- **Button Animations**: Hover effects with transform and shadow changes
- **Color Scheme**: Professional purple gradient theme
- **Mobile-First Design**: Optimized for all screen sizes

### 🚀 Technical Features
- **Template Inheritance**: Clean, maintainable code structure
- **Django Forms**: Proper form handling with validation
- **URL Routing**: Clean URL structure
- **Static Styling**: All styles included inline for easy deployment

## Getting Started

1. Navigate to the project directory:
   ```bash
   cd "3.BookStore Project/bookstore"
   ```

2. Run the development server:
   ```bash
   python manage.py runserver
   ```

3. Visit `http://127.0.0.1:8000/` in your browser

## Project Structure

```
bookstore/
├── books/
│   ├── templates/books/
│   │   ├── layout.html      # Base template with all styling
│   │   ├── home.html        # Welcome page
│   │   ├── book_list.html   # Book catalog
│   │   ├── add_book.html    # Add new book form
│   │   ├── contact.html     # Contact form
│   │   └── thank_you.html   # Success page
│   ├── models.py            # Book model
│   ├── forms.py             # Contact and Book forms
│   ├── views.py             # View functions
│   └── urls.py              # URL patterns
├── bookstore/
│   ├── settings.py          # Django settings
│   └── urls.py              # Main URL configuration
└── manage.py                # Django management script
```

## Customization

### Colors
The main color scheme uses:
- Primary: `#667eea` (Purple)
- Secondary: `#764ba2` (Darker Purple)
- Success: `#28a745` (Green)
- Warning: `#ffc107` (Yellow)

### Adding Books
Use the Django admin interface or add books directly to the database:
```python
from books.models import Book
Book.objects.create(title="Your Book Title", author="Author Name")
```

## Browser Support
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers

## License
This project is open source and available under the MIT License. 