import argparse
from datetime import datetime
from gtts import gTTS
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont
import random
import re
import requests
import shutil
import subprocess
import textwrap
import time





REQUESTS_HEADER = {"User-agent": "Mozilla/5.0 (Linux; U; Android 2.2; de-de; HTC Magic Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"}

with open("filter.json") as f:
    FILTER = json.load(f)

with open("config.json") as f:
    config = json.load(f)
    INTRO_FILE = config["intro"]
    OUTRO_FILE = config["outro"]
    TRANSITION_FILE = config["transition"]
    SUBREDDITS = config["subreddits"]
    MUSIC_FOLDER = config["music_folder"]
    MUSIC_VOLUME = config["music_volume"]
    SORT_BY = config["sort_by"]
    COUNT = config["count"]
    MIN_LENGTH = config["min_video_length"]
    UPVOTE_THRESHOLD = config["upvote_threshold"]
    TTS_COOLDOWN = config["tts_cooldown"]
    VOICE = config["voice"]
    PROFANITY_FILTER = config["ad_friendly_filter"]
    NSFW_FILTER = config["include_nsfw_posts"]
    ENDLESS = True if COUNT < 1 else False
    VIDEO_CODEC = config["ffmpeg_c:v"]
    AUDIO_CODEC = config["ffmpeg_c:a"]
    PIXEL_FORMAT = config["ffmpeg_pix_fmt"]
    AUDIO_SAMPLING_RATE = config["ffmpeg_ar"]
    MIN_COMMENT_LENGTH = config["min_comment_length"]
    MAX_COMMENT_LENGTH = config["max_comment_length"]
    print(TRANSITION_FILE)


HEADER_FONT = ImageFont.truetype("font.ttf", 26)
TEXT_FONT = ImageFont.truetype("font.ttf", 34)


COMMENT_COUNTER = -1
LENGTH = 0


def pick_reddit_post():
    global NSFW_FILTER
    askreddit_json = requests.get("https://www.reddit.com/r/%s/%s.json?count=100" % (random.choice(SUBREDDITS), SORT_BY), headers=REQUESTS_HEADER).text
    potential_posts_list = json.loads(askreddit_json)["data"]["children"]
    for p in potential_posts_list:
        if p["data"]["pinned"] or p["data"]["stickied"] or (p["data"]["over_18"] and NSFW_FILTER) or p["data"]["ups"] < UPVOTE_THRESHOLD:
            potential_posts_list.remove(p)
    picked_post_url = random.choice(potential_posts_list)["data"]["url"]
    picked_post = requests.get(picked_post_url[:-1] + ".json", headers=REQUESTS_HEADER).text
    picked_post_json = json.loads(picked_post)
    picked_post_json[0]["data"]["children"][0]["data"]["title"] = filter(picked_post_json[0]["data"]["children"][0]["data"]["title"])
    return picked_post_json


def generate_TTS(text):
    global LENGTH
    filename = os.path.join("tts", "%s.mp3" % str(COMMENT_COUNTER))
    edited_text = text.replace("*", "").replace("_", "")
    if VOICE.lower() == "google":
        print("Generating TTS (Google)")
        tts = gTTS(text)
        tts.save(filename)
    else:
        print("Generating TTS (Brian)")
        tts = requests.get("https://api.streamelements.com/kappa/v2/speech?voice=Brian&text=%s" % text)
        with open(filename, "wb") as f:
            f.write(tts.content)
    LENGTH += get_length(filename)
    if TRANSITION_FILE is not None:
        LENGTH += get_length(TRANSITION_FILE)



# thanks to SingleNegationElimination on StackOverflow!
def get_length(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of",
            "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    return float(result.stdout)


def filter(text):
    text = re.sub(r"\[(.+)\]\(.+\)", r"\1", text)
    if PROFANITY_FILTER:
        for a in FILTER.keys():
            text = text.replace(a, FILTER[a])
    return text


def truncate(text):
    new_text = text.replace("\n", " ")
    if len(text) > 128:
        new_text = new_text[:128]
        new_text += "..."
    return new_text


def generate_image(author, points, text, title=False):
    print("Generating image")
    header = "u/%s | %s points" % (author, str(points))
    if points >= 1000:
        header = "u/%s | %.1fk points" % (author, points/1000)
    background = Image.new("RGBA", (1920, 1080), (26, 26, 26, 255))
    draw = ImageDraw.Draw(background)
    # we have to do this weird replace thing because textwrap deletes exisiting newlines
    text_block = "\n".join(textwrap.wrap(text.replace("\n", "#=#"), width=120)).replace("#=#", "\n")
    header_size = draw.textsize(header, HEADER_FONT)
    text_size = draw.textsize(text_block, TEXT_FONT)
    total_size = (max(header_size[0], text_size[0]), header_size[1] + text_size[1] + 12)
    text_im = Image.new("RGBA", total_size, (26, 26, 26, 255))
    text_draw = ImageDraw.Draw(text_im);
    text_draw.text((0, 0), header, font=HEADER_FONT, fill=(86, 86, 86, 255))
    text_draw.text((0, header_size[1]), text_block, font=TEXT_FONT, fill=(255, 255, 255, 255))
    background.paste(text_im, (int((background.size[0] - total_size[0]) / 2), int((background.size[1] - total_size[1]) / 2)))
    background.save(os.path.join("img", "%s.png" % str(COMMENT_COUNTER)))


# master function that generates the whole video
def generate_video():
    global COMMENT_COUNTER
    global LENGTH
    global MIN_LENGTH
    global REMOVE_TMP
    used_numbers = [-1]
    if not os.path.exists("tts"):
    	os.mkdir("tts")
    if not os.path.exists("img"):
        os.mkdir("img")
    if not os.path.exists("vid"):
        os.mkdir("vid")
    start_time = datetime.now()
    if INTRO_FILE is not None:
        LENGTH += get_length(INTRO_FILE)
    if OUTRO_FILE is not None:
        LENGTH += get_length(OUTRO_FILE)
    if TRANSITION_FILE is not None:
        LENGTH += get_length(TRANSITION_FILE)
    reddit_post = pick_reddit_post()
    print("Picked thread \"%s\"" % reddit_post[0]["data"]["children"][0]["data"]["title"])
    generate_image(filter(reddit_post[0]["data"]["children"][0]["data"]["author"]), reddit_post[0]["data"]["children"][0]["data"]["ups"], filter(reddit_post[0]["data"]["children"][0]["data"]["title"]))
    generate_TTS(reddit_post[0]["data"]["children"][0]["data"]["title"])
    print("Waiting %s seconds for TTS" % str(TTS_COOLDOWN))
    time.sleep(TTS_COOLDOWN)
    COMMENT_COUNTER += 1
    print("Reached length: %s" % str(LENGTH))
    while LENGTH < MIN_LENGTH:
        comment = reddit_post[1]["data"]["children"][COMMENT_COUNTER]
        COMMENT_COUNTER += 1
        if COMMENT_COUNTER >= len(reddit_post[1]["data"]["children"]):
            print("Out of comments!")
            break
        try:
            if comment["data"]["author"] == "AutoModerator":
                print("Discarding AutoModerator's comment")
                continue
        # if this happens, we reached a weird comment-like thing in the comments marking the end
        except:
            print("Out of comments!")
            break
        if len(comment["data"]["body"]) > MAX_COMMENT_LENGTH:
            print("Discarding comment #%s because it is too long" % COMMENT_COUNTER)
            continue
        if len(comment["data"]["body"]) < MIN_COMMENT_LENGTH:
            print("Discarding comment #%s because it is too short" % COMMENT_COUNTER)
            continue
        comment_text = filter(comment["data"]["body"])
        print("Picked comment #%s: %s" % (COMMENT_COUNTER, truncate(comment_text)))
        generate_image(filter(comment["data"]["author"]), comment["data"]["ups"], comment_text)
        generate_TTS(comment_text)
        print("Timeout for %s seconds to avoid TTS rate-limiting" % str(TTS_COOLDOWN))
        time.sleep(TTS_COOLDOWN)
        used_numbers.append(COMMENT_COUNTER)
        print("Length reached: %s seconds" % str(LENGTH))
    # stitch it all together
    # first we want to make clips of every comment, then we stich all those clips together (including intro, outro and transition if applicable)
    intro_conv = os.path.join("vid", "intro.flv")
    transition_conv = os.path.join("vid", "transition.flv")
    outro_conv = os.path.join("vid", "outro.flv")
    with open("content_list.txt", "a") as f:
        print("Creating clips out of the comments")
        if TRANSITION_FILE is not None and not os.path.exists(transition_conv):
            f.write("file '%s'\n" % transition_conv)
        for i in used_numbers:
            if(os.path.exists(os.path.join("tts", "%s.mp3" % str(i)))):
                print("Building clip #" + str(i))
                img_path = os.path.join("img", "%s.png" % str(i))
                tts_path = os.path.join("tts", "%s.mp3" % str(i))
                vid_path = os.path.join("vid", "%s.flv" % str(i))
                subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", img_path,
                        "-i", tts_path, "-c:v", VIDEO_CODEC, "-tune", "stillimage", "-c:a", AUDIO_CODEC, "-ar", AUDIO_SAMPLING_RATE, "-shortest", "-pix_fmt", PIXEL_FORMAT,
                        "-r", "30", "-t", str(get_length(tts_path)), vid_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
                f.write("file '%s'\n" % vid_path)
                if TRANSITION_FILE is not None and os.path.exists(TRANSITION_FILE):
                    f.write("file '%s'\n" % transition_conv)
    if INTRO_FILE is not None and not os.path.exists(intro_conv):
        print("Converting intro into the same format")
        subprocess.run(["ffmpeg", "-y", "-i", INTRO_FILE, "-vf", "scale=1920:1080", "-aspect", "1920:1080",
                "-c:v", VIDEO_CODEC, "-s", "1920x1080", "-c:a", AUDIO_CODEC, "-ar", AUDIO_SAMPLING_RATE, "-shortest", "-pix_fmt", PIXEL_FORMAT, "-r", "30",
                intro_conv],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
    if TRANSITION_FILE is not None and not os.path.exists(transition_conv):
        print("Converting transition into the same format")
        subprocess.run(["ffmpeg", "-y", "-i", TRANSITION_FILE, "-vf", "scale=1920:1080", "-aspect", "1920:1080",
                "-c:v", VIDEO_CODEC, "-s", "1920x1080", "-c:a", AUDIO_CODEC, "-ar", AUDIO_SAMPLING_RATE, "-shortest", "-pix_fmt", PIXEL_FORMAT, "-r", "30", 
                transition_conv],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
    if OUTRO_FILE is not None and not os.path.exists(outro_conv):
        print("Converting outro into the same format")
        subprocess.run(["ffmpeg", "-y", "-i", OUTRO_FILE, "-vf", "scale=1920:1080", "-aspect", "1920:1080",
                "-c:v", VIDEO_CODEC, "-s", "1920x1080", "-c:a", AUDIO_CODEC, "-ar", AUDIO_SAMPLING_RATE, "-shortest", "-pix_fmt", PIXEL_FORMAT, "-r", "30", 
                outro_conv],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
    print("Stitching the clips together")
    subprocess.run(["ffmpeg", "-y", "-safe", "0", "-f", "concat", "-i", "content_list.txt", "-c", "copy", os.path.join("vid", "content.flv")],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    music_file = None
    if MUSIC_FOLDER != None:
        if os.path.isfile(MUSIC_FOLDER):
            music_file = MUSIC_FOLDER
        elif os.path.isdir(MUSIC_FOLDER):
            music_file = os.path.join(MUSIC_FOLDER, random.choice(os.listdir(MUSIC_FOLDER)))
        else:
            print("Unable to locate music, skipping adding the music.")
    if music_file != None:
        print("Looping the music (unelegantly, sorry :/)")
        vid_length = get_length(os.path.join("vid", "content.flv"))
        loops = math.ceil(vid_length / get_length(music_file))
        with open("music_loop.txt", "a") as f:
            for i in range(0, loops):
                f.write("file '%s'\n" % music_file)
        subprocess.run(["ffmpeg", "-y", "-t", str(vid_length), "-f", "concat", "-safe", "0", "-i", "music_loop.txt", "-t", str(vid_length), "-filter:a", "volume=%s" % str(MUSIC_VOLUME), "-c:a", "aac", os.path.join("vid", "looped.m4a")],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        print("Putting the music into the video")
        subprocess.run(["ffmpeg", "-y", "-i", os.path.join("vid", "content.flv"), "-i", os.path.join("vid", "looped.m4a"),
                "-filter_complex", "[1:0]volume=1[a1];[0:a][a1]amix=inputs=2:duration=first", "-map", "0:v:0", "-c:v", "copy", "-c:a", "aac", os.path.join("vid", "content_music.flv")],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        os.remove(os.path.join("vid", "content.flv"))
        os.rename(os.path.join("vid", "content_music.flv"), os.path.join("vid", "content.flv"))
    # apparently we have to do this to "fix" the video?
    subprocess.run(["ffmpeg", "-i", os.path.join("vid", "content.flv"), "-c", "copy", os.path.join("vid", "content_fixed.flv")],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    print("Finishing the video")
    with open("list.txt", "a") as f:
        if INTRO_FILE is not None:
            f.write("file '%s'\n" % intro_conv)
        f.write("file '%s'\n" % os.path.join("vid", "content_fixed.flv"))
        if OUTRO_FILE is not None:
            f.write("file '%s'\n" % outro_conv)
    subprocess.run(["ffmpeg", "-y", "-safe", "0", "-f", "concat", "-i", "list.txt", "-c", "copy", reddit_post[0]["data"]["children"][0]["data"]["title"] + ".flv"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
    print("Deleting temporary folders and files")
    shutil.rmtree("tts")
    shutil.rmtree("img")
    shutil.rmtree("vid")
    os.remove("list.txt")
    os.remove("content_list.txt")
    if os.path.exists("music_loop.txt"):
        os.remove("music_loop.txt")
    print("Done, and it only took %s! Have fun with your new video! :)" % str(datetime.now() - start_time))
    COMMENT_COUNTER = -1
    LENGTH = 0


if __name__ == "__main__":
    video_counter = 0
    print("Starting...")
    if ENDLESS:
        print("Warning! Endless mode activated!")
        while True:
            print("Starting video #%s" % str(video_counter + 1))
            generate_video()
            video_counter += 1
    else:
        while video_counter < COUNT:
            print("Starting video #%s" % str(video_counter + 1))
            generate_video()
            video_counter += 1

