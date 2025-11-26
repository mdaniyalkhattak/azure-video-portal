from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from storage import upload_video, list_videos, get_video, add_comment, delete_video

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = Config.SECRET_KEY

    @app.route("/")
    def index():
        q = (request.args.get("q") or "").strip().lower()
        videos = list_videos()
        if q:
            videos = [v for v in videos if q in v.title.lower()]
        return render_template("index.html", videos=videos, q=q)

    @app.route("/upload", methods=["POST"])
    def upload():
        file = request.files.get("video")
        title = (request.form.get("title") or "").strip()

        if not file or file.filename == "":
            flash("Please select a video file", "error")
            return redirect(url_for("index"))

        try:
            video = upload_video(file, title)
        except Exception as exc:
            app.logger.exception("Error uploading video")
            flash(f"Error uploading video: {exc}", "error")
            return redirect(url_for("index"))

        flash("Video uploaded successfully", "success")
        return redirect(url_for("video_detail", video_id=video.id))

    @app.route("/video/<video_id>")
    def video_detail(video_id):
        video = get_video(video_id)
        if not video:
            flash("Video not found", "error")
            return redirect(url_for("index"))
        return render_template("video_detail.html", video=video)

    @app.route("/video/<video_id>/comment", methods=["POST"])
    def add_comment_route(video_id):
        author = (request.form.get("author") or "Anonymous").strip() or "Anonymous"
        text = (request.form.get("text") or "").strip()

        if not text:
            flash("Comment text cannot be empty", "error")
            return redirect(url_for("video_detail", video_id=video_id))

        video = add_comment(video_id, author, text)
        if not video:
            flash("Video not found", "error")
            return redirect(url_for("index"))

        flash("Comment added", "success")
        return redirect(url_for("video_detail", video_id=video_id))

    @app.route("/video/<video_id>/delete", methods=["POST"])
    def delete_video_route(video_id):
        ok = delete_video(video_id)
        if not ok:
            flash("Video not found", "error")
        else:
            flash("Video deleted", "success")
        return redirect(url_for("index"))

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
