from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///elearning.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="user")  # user, tutor, creator
    wallet_balance = db.Column(db.Float, default=0.0)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    video_url = db.Column(db.String(200), nullable=False)
    reward_tokens = db.Column(db.Float, default=10.0)
    tutor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)
    watched = db.Column(db.Boolean, default=False)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    video_url = db.Column(db.String(200), nullable=False)
    reward_tokens = db.Column(db.Float, default=5.0)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class AdInteraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    interaction_type = db.Column(db.String(50), nullable=False)  # View, Click, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    ad = db.relationship('Ad', back_populates="interactions")
    user = db.relationship('User', back_populates="interactions")


class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    media_url = db.Column(db.String(200), nullable=True)  # For storing image/video URL
    media_type = db.Column(db.String(50), nullable=False)  # "image" or "video"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    interactions = db.relationship('AdInteraction', back_populates="ad")
    user = db.relationship('User', back_populates="ads")


class ContentView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)
    watched = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route("/")
def home():
    courses = Course.query.all()
    contents = Content.query.all()
    return render_template("index.html", courses=courses, contents=contents, user=current_user)





@app.route("/benefit")
def benefit():
    return render_template("benefit.html", user=current_user)





@app.route('/api/recharge/airtime', methods=['POST'])
def recharge_airtime():
    data = request.get_json()
    
    phone_number = data.get('phone')
    network = data.get('network')
    amount = data.get('amount')
    
    # Basic validation for the incoming data
    if not phone_number or not network or not amount:
        return jsonify({'success': False, 'message': 'Invalid data. Please provide all required fields.'}), 400
    
    if not isinstance(amount, (int, float)) or amount <= 0:
        return jsonify({'success': False, 'message': 'Invalid amount.'}), 400
    
    # Simulating Airtime Recharge Logic (In real-world, you would integrate with a payment gateway)
    success = random.choice([True, False])  # Simulating success or failure randomly
    
    if success:
        return jsonify({'success': True, 'message': 'Airtime recharge successful!'})
    else:
        return jsonify({'success': False, 'message': 'Airtime recharge failed. Please try again later.'}), 500

# Simple route for Data Recharge
@app.route('/api/recharge/data', methods=['POST'])
def recharge_data():
    data = request.get_json()
    
    phone_number = data.get('phone')
    network = data.get('network')
    plan = data.get('plan')
    
    # Basic validation for the incoming data
    if not phone_number or not network or not plan:
        return jsonify({'success': False, 'message': 'Invalid data. Please provide all required fields.'}), 400
    
    # Simulating Data Plan Recharge Logic (In real-world, you would integrate with a data provider)
    success = random.choice([True, False])  # Simulating success or failure randomly
    
    if success:
        return jsonify({'success': True, 'message': 'Data plan recharge successful!'})
    else:
        return jsonify({'success': False, 'message': 'Data plan recharge failed. Please try again later.'}), 500















@app.route("/")
def home():
    courses = Course.query.all()
    contents = Content.query.all()
    return render_template("index.html", courses=courses, contents=contents, user=current_user)





@app.route("/ads/click/<int:ad_id>", methods=["POST"])
@login_required
def ad_click(ad_id):
    ad = Ad.query.get_or_404(ad_id)
    
    # Log user click interaction
    new_interaction = AdInteraction(
        ad_id=ad.id,
        user_id=current_user.id,
        interaction_type="click"
    )
    db.session.add(new_interaction)
    db.session.commit()

    flash("Ad clicked successfully!", "success")
    return redirect(ad.media_url)  # Redirect to the ad's media content (e.g., website, video page)




@app.route("/ads/view", methods=["GET"])
@login_required
def view_ads():
    ads = Ad.query.all()
    ads_data = []

    for ad in ads:
        ad_data = {
            "id": ad.id,
            "title": ad.title,
            "description": ad.description,
            "media_url": ad.media_url,
            "media_type": ad.media_type,
            "user_id": ad.user_id,
        }
        
        # Track the user interaction (view)
        new_interaction = AdInteraction(
            ad_id=ad.id,
            user_id=current_user.id,
            interaction_type="view"
        )
        db.session.add(new_interaction)
        db.session.commit()

        ads_data.append(ad_data)

    return jsonify(ads_data)



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
        role = request.form.get("role", "user")  # Default to user if no role is selected

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        current_user.username = request.form["username"]
        current_user.email = request.form["email"]
        if "password" in request.form and request.form["password"]:
            current_user.password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
        db.session.commit()
        flash("Profile updated successfully!", "success")
    return render_template("settings.html", user=current_user)



@app.route("/upload-ad", methods=["GET", "POST"])
@login_required
def upload_ad():
    if current_user.role != "admin":
        flash("Only admins can upload ads!", "danger")
        return redirect(url_for("home"))
    if request.method == "POST":
        new_ad = Ad(
            title=request.form["title"],
            description=request.form["description"],
            image_url=request.files["image"].filename if "image" in request.files else None,
            user_id=current_user.id,
        )
        if new_ad.image_url:
            request.files["image"].save(os.path.join(app.config["UPLOAD_FOLDER"], new_ad.image_url))
        db.session.add(new_ad)
        db.session.commit()
        flash("Ad uploaded successfully!", "success")
    return render_template("upload_ad.html")





@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid credentials!", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/upload-course", methods=["GET", "POST"])
@login_required
def upload_course():
    if current_user.role != "tutor":
        flash("Only tutors can upload courses!", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        price = float(request.form["price"])
        video = request.files["video"]
        reward_tokens = float(request.form.get("reward_tokens", 10.0))

        if video:
            video_path = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
            video.save(video_path)

            new_course = Course(
                title=title,
                description=description,
                price=price,
                video_url=video_path,
                reward_tokens=reward_tokens,
                tutor_id=current_user.id,
            )
            db.session.add(new_course)
            db.session.commit()
            flash("Course uploaded successfully!", "success")
            return redirect(url_for("home"))

    return render_template("upload_course.html")

@app.route("/upload-content", methods=["GET", "POST"])
@login_required
def upload_content():
    if current_user.role != "creator":
        flash("Only content creators can upload content!", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        video = request.files["video"]
        reward_tokens = float(request.form.get("reward_tokens", 5.0))

        if video:
            video_path = os.path.join(app.config["UPLOAD_FOLDER"], video.filename)
            video.save(video_path)

            new_content = Content(
                title=title,
                description=description,
                video_url=video_path,
                reward_tokens=reward_tokens,
                creator_id=current_user.id,
            )
            db.session.add(new_content)
            db.session.commit()
            flash("Content uploaded successfully!", "success")
            return redirect(url_for("home"))

    return render_template("upload_content.html")

@app.route("/wallet")
@login_required
def wallet():
    return render_template("wallet.html", user=current_user)

@app.route("/topup", methods=["POST"])
@login_required
def topup():
    amount = float(request.form["amount"])
    current_user.wallet_balance += amount
    db.session.commit()
    flash(f"Wallet topped up with {amount} successfully!", "success")
    return redirect(url_for("wallet"))

@app.route("/course/<int:course_id>")
@login_required
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    return render_template("course_detail.html", course=course, enrollment=enrollment)

@app.route("/content/<int:content_id>")
@login_required
def content_detail(content_id):
    content = Content.query.get_or_404(content_id)
    view = ContentView.query.filter_by(user_id=current_user.id, content_id=content_id).first()
    return render_template("content_detail.html", content=content, view=view)

# Database Initialization
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
    app.run(debug=True)
