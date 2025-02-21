from flask import Flask, render_template, request, jsonify
import re
import datetime

app = Flask(__name__)

# Validators
def multi_language_string_validator(string):
    # Define patterns for specific scripts
    patterns = {
        "Latin": r'[A-Za-z0-9\s\.,!?]+',  # Covers basic Latin characters
        "Cyrillic": r'[\u0400-\u04FF\s\.,!?]+',  # Covers Russian, Ukrainian, etc.
        "Devanagari": r'[\u0900-\u097F\s]+',  # Covers Hindi, Sanskrit, Marathi, etc.
        "Arabic": r'[\u0600-\u06FF\s\.,!?]+',  # Covers Arabic script
        "Chinese": r'[\u4E00-\u9FFF\s\.,!?]+',  # Covers most Chinese characters
        "Japanese": r'[\u3040-\u30FF\u4E00-\u9FFF\s\.,!?]+',  # Covers Hiragana, Katakana, and Kanji
        "Korean": r'[\uAC00-\uD7AF\s\.,!?]+',  # Covers Hangul syllables
        "Hebrew": r'[\u0590-\u05FF\s\.,!?]+',  # Covers Hebrew script
        "Greek": r'[\u0370-\u03FF\s\.,!?]+',  # Covers Greek alphabet
        "Thai": r'[\u0E00-\u0E7F\s\.,!?]+',  # Covers Thai script
        "Tamil": r'[\u0B80-\u0BFF\s\.,!?]+',  # Covers Tamil script
        "Bengali": r'[\u0980-\u09FF\s\.,!?]+',  # Covers Bengali script
        "Telugu": r'[\u0C00-\u0C7F\s\.,!?]+',  # Covers Telugu script
        "Gujarati": r'[\u0A80-\u0AFF\s\.,!?]+',  # Covers Gujarati script
        "Punjabi (Gurmukhi)": r'[\u0A00-\u0A7F\s\.,!?]+',  # Covers Gurmukhi script
        "Kannada": r'[\u0C80-\u0CFF\s\.,!?]+',  # Covers Kannada script
        "Myanmar": r'[\u1000-\u109F\s\.,!?]+',  # Covers Burmese/Myanmar script
        "Georgian": r'[\u10A0-\u10FF\s\.,!?]+',  # Covers Georgian script
        "Ethiopic": r'[\u1200-\u137F\s\.,!?]+',  # Covers Amharic, Tigrinya, etc.
        "Sinhala": r'[\u0D80-\u0DFF\s\.,!?]+',  # Covers Sinhala script
    }

    detected_scripts = []
    for script, pattern in patterns.items():
        if re.search(pattern, string):
            detected_scripts.append(script)

    # Flag as invalid if more than one script is detected
    if len(detected_scripts) > 1:
        return False, f"Mixed scripts detected: {', '.join(detected_scripts)}"

    return True, f"Valid {detected_scripts[0]} string" if detected_scripts else "No matching script"

'''# Test cases
print(multi_language_string_validator("ನಮಸ್ಕಾರ"))  # Valid Kannada string
print(multi_language_string_validator("Hello ನಮಸ್ಕಾರ"))  # Mixed scripts
print(multi_language_string_validator("ಹೆಚ್ಚು ದಿವಸ"))  # Valid Kannada string
'''

def username_handle_validator(username, platform="general"):
    # Reserved usernames that are restricted across all platforms
    reserved_usernames = ["admin", "support", "root", "system", "test", "superuser", "null", "none"]

    if username.lower() in reserved_usernames:
        return False, f"'{username}' is a reserved username and cannot be used"

    # Patterns for specific platforms
    patterns = {
        "general": r'^[a-zA-Z][a-zA-Z0-9_]{2,14}$',  # Letters only, length 3-15
        "twitter": r'^[a-zA-Z0-9_]{1,15}$',  # Letters, digits, underscores, length 1-15
        "instagram": r'^[a-zA-Z0-9._]{1,30}$',  # Allows dots and underscores, length 1-30
        "github": r'^[a-zA-Z0-9-]{1,39}$',  # Letters, digits, dashes, length 1-39
        "linkedin": r'^[a-zA-Z0-9-]{3,100}$',  # Letters, digits, dashes, length 3-100
        "snapchat": r'^[a-zA-Z0-9._-]{3,15}$',  # Letters, digits, dots, dashes, underscores, length 3-15
        "tiktok": r'^[a-zA-Z0-9._]{2,24}$',  # Letters, digits, dots, underscores, length 2-24
        "youtube": r'^[a-zA-Z0-9_-]{3,20}$',  # Letters, digits, underscores, dashes, length 3-20
        "custom": r'^[a-zA-Z][a-zA-Z0-9._-]{4,30}$'  # Custom rule: allows dots, dashes, underscores, length 5-30
    }

    # Handle unknown platforms
    if platform not in patterns:
        return False, f"Unknown platform: '{platform}'"

    # Check the username against the selected platform's pattern
    if re.match(patterns[platform], username):
        return True, f"Valid username for {platform}"
    else:
        return False, f"Invalid username for {platform}. Ensure it meets the platform's rules."

'''# General username
print(username_handle_validator("user123", "general"))  # Valid username for general

# Twitter-specific validation
print(username_handle_validator("valid_user_12", "twitter"))  # Valid username for twitter
print(username_handle_validator("invalid.user", "twitter"))  # Invalid username for twitter

# GitHub validation
print(username_handle_validator("valid-username", "github"))  # Valid username for github
print(username_handle_validator("invalid.username", "github"))  # Invalid username for github

# Reserved username check
print(username_handle_validator("Admin", "general"))  # 'Admin' is a reserved username
'''

def date_format_validator(date):
    # List of supported date formats
    formats = [
        "%m/%d/%Y",  # MM/DD/YYYY
        "%d-%m-%Y",  # DD-MM-YYYY
        "%Y.%m.%d",  # YYYY.MM.DD
        "%d.%m.%Y",  # DD.MM.YYYY
        "%Y/%m/%d",  # YYYY/MM/DD
        "%B %d, %Y",  # Month DD, YYYY (e.g., January 01, 2023)
        "%d %B %Y",  # DD Month YYYY (e.g., 01 January 2023)
        "%Y-%m-%d",  # ISO standard YYYY-MM-DD
        "%d/%m/%Y",  # DD/MM/YYYY
        "%m-%d-%Y",  # MM-DD-YYYY
    ]

    for fmt in formats:
        try:
            # Try to parse the date using the current format
            parsed_date = datetime.datetime.strptime(date, fmt)

            # Check for extra boundary conditions (e.g., leap years)
            if fmt in ["%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y"] and (parsed_date.day > 31 or parsed_date.month > 12):
                return False, f"Invalid day or month in date '{date}'"

            return True, f"Valid date in format {fmt}"
        except ValueError:
            continue

    # If no formats matched
    return False, "Invalid date or format"

'''# Example Test Cases
print(date_format_validator("01/15/2023"))  # Valid date in format %m/%d/%Y
print(date_format_validator("15-01-2023"))  # Valid date in format %d-%m-%Y
print(date_format_validator("2023.01.15"))  # Valid date in format %Y.%m.%d
print(date_format_validator("31-02-2023"))  # Invalid date or format
print(date_format_validator("February 29, 2024"))  # Valid date in format %B %d, %Y (leap year check)
'''
def html_xml_tag_validator(html):
    stack = []
    pattern = r'<(/?)(\w+)(?:\s+[^>]*)?>'
    for match in re.finditer(pattern, html):
        is_closing = match.group(1) == '/'
        tag = match.group(2)

        if is_closing:
            if not stack or stack[-1] != tag:
                return False, f"Mismatched closing tag </{tag}>"
            stack.pop()
        else:
            stack.append(tag)

    # Check for unclosed tags
    if stack:
        return False, f"Unclosed tags: {', '.join(stack)}"

    return True, "Valid HTML/XML"


def email_validator(email):
    # Regular expression for email validation
    email_pattern = (
        r"^(?!.*\.\.)"  # Prevent consecutive dots
        r"[a-zA-Z0-9._%+-]+"  # Username part
        r"@[a-zA-Z0-9.-]+"  # Domain name
        r"\.[a-zA-Z]{2,}$"  # Top-level domain (e.g., .com, .org)
    )

    # Check against email pattern
    if not re.match(email_pattern, email):
        return False, "Invalid email format"

    # Check for valid top-level domain
    tld_pattern = r'\.[a-zA-Z]{2,}$'
    if not re.search(tld_pattern, email):
        return False, "Missing or invalid top-level domain (e.g., .com, .org)"

    # Split email into username and domain parts
    try:
        username, domain = email.split('@')
    except ValueError:
        return False, "Email must contain exactly one '@' symbol"

    # Reserved domains check
    reserved_domains = ['example.com', 'test.com', 'invalid.com']
    if domain in reserved_domains:
        return False, f"The domain '{domain}' is reserved and cannot be used"

    # Username-specific checks
    if username.startswith('-') or username.endswith('-'):
        return False, "Username cannot start or end with a hyphen (-)"
    if len(username) > 64:
        return False, "Username exceeds 64 characters"

    # Domain-specific checks
    if domain.startswith('-') or domain.endswith('-'):
        return False, "Domain cannot start or end with a hyphen (-)"
    if len(domain) > 255:
        return False, "Domain exceeds 255 characters"

    # Subdomain checks
    subdomains = domain.split('.')
    for sub in subdomains:
        if len(sub) > 63:
            return False, f"Subdomain '{sub}' exceeds 63 characters"
        if not re.match(r"^[a-zA-Z0-9-]+$", sub):
            return False, f"Subdomain '{sub}' contains invalid characters"

    return True, "Valid email address"

'''# Test cases
print(email_validator("john.doe@example.com"))  # Valid
print(email_validator("jane_doe@sub.example.com"))  # Valid
print(email_validator("invalid..email@domain.com"))  # Invalid (consecutive dots)
print(email_validator("user@invalid-domain-.com"))  # Invalid (hyphen at the end of domain)
print(email_validator("user@example.com"))  # Reserved domain
print(email_validator("user@domain_with_special_chars!.com"))  # Invalid domain
print(email_validator("long_username_" + "a" * 55 + "@example.com"))  # Invalid (username too long)
print(email_validator("user@long-domain-name-" + "a" * 250 + ".com"))  # Invalid (domain too long)
print(email_validator("user@subdomain.exceeding63characters-" + "a" * 50 + ".com"))  # Invalid (subdomain too long)
'''

# Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/validate', methods=['POST'])
def validate():
    data_type = request.form['type']
    user_input = request.form['input']

    if data_type == 'language':
        is_valid, message = multi_language_string_validator(user_input)
    elif data_type == 'username':
        platform = request.form.get('platform', 'general')  # Optional field for username validator
        is_valid, message = username_handle_validator(user_input, platform)
    elif data_type == 'date':
        is_valid, message = date_format_validator(user_input)
    elif data_type == 'html':
        is_valid, message = html_xml_tag_validator(user_input)
    elif data_type == 'email':
        is_valid, message = email_validator(user_input)
    else:
        is_valid, message = False, "Invalid validation type"

    # Return JSON response
    return jsonify({'is_valid': is_valid, 'message': message})


if __name__ == '__main__':
    app.run(debug=True)
