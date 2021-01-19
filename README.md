# rttsvg
Reddit TTS Video Generator

## About

This is a little Python script that can generate average Reddit TTS videos (you've surely seen generic r/AskReddit videos in your recommendations) within minutes!

The script is designed to be easily usable and configurable and supports adding an intro, outro and transitions along with background music, to give your generic Reddit videos more "personality". The video codec is freely configurable, so hardware acceleration is also possible, if your hardware and ffmpeg supports it.

## Requirements

You need [ffmpeg](https://ffmpeg.org/), as the script makes heavy use of it for generating the video.

You'll also need the following Python packages (available with ``pip``):

``gtts>=2.2.1``

``pillow>=7.2.0``

You can also use the ``requirements.txt`` to automatically install all the necessary packages.

## Configuration

All configuration happens in ``config.json``. You can change the following options:

``intro``: Path to the intro video, if null, no intro is used.

``outro``: Path to the outro video, if null, no outro is used.

``transition``: Path to the transition video, if null, no transition is used.

``subreddits``: List of subreddits to look for posts on. When generating a video, a random entry will be chosen.

``music_folder``: Path to a single MP3 file or folder of MP3 files (yes, they have to be MP3, sorry). When generating a video, the file or a random file will be chosen to loop for the whole video.

``music_volume``: Volume of the background music. Float between 0-1.

``sort_by``: What the generator should sort the reddit posts by.

``count``: How many videos should be generated. If < 1, then the script will generate videos infinitely. Possible values are ``top`` (default and recommended), ``new``, ``controversial`` and ``rising``.

``min_video_length``: The minimum length in seconds the generated videos. Videos can be shorter if too few comments reach the requirements below. Recommended value is 600 for that juicy YouTube ad revenue.

``upvote_threshold``: The minimum amounts of upvote a **post** (not a comment) has to have for it to be considered.

``voice``: TTS Voice to be used. ``google`` has a lower recommended cooldown and is more reliable, ``brian`` is pretty unreliable concerning rate-limiting (or not being blocked right off the bat) but useful for the authentic generic AskReddit video experience™.

``tts_cooldown``: Cooldown in seconds between TTS requests. Recommended values are 6 for ``google``, atleast 10 for ``brian``.

``ad_friendly_filter``: Replaces bad words with more ~~ad~~ family friendly words. Configurable in ``filter.json``.

``include_nsfw_posts``: If true, NSFW posts can be considered for a video.

``min_comment_length``: The minimum amount of characters a comment must have for it to be considered into the video.

``max_comment_length``: The maximum amount of characters a comment must have for it to be considered into the video.

``ffmpeg_c:v``: The argument for the ``c:v`` (video codec) option for ffmpeg. ``libx264`` is widely supported, but is software-based, so it might be a bit slow.

``ffmpeg_c:a``: The argument for the ``c:a`` (audio codec) option for ffmpeg. Best to leave it at ``aac``.

``ffmpeg_pix_fmt``: The argument for the ``pix_fmt`` (pixel format) option for ffmpeg. Best to leave it at ``yuv420p``.

``ffmpeg_ar``: The argument for the ``ar`` (audio sampling rate) option for ffmpeg. Best to leave it at ``22050``, since the TTS MP3s also have that sampling rate.

## Todo (not in a particular order)

- Code cleanup (lol)
- Make the include_nsfw_posts option actually work
- Ability to get more reddit posts and comments to avoid running out of them
- Automatic video title generation
- Automatic thumbnail generation
- Automatic (scheduled?) upload to YouTube
- More TTS voices (and/or making Brian more reliable)
- ~~Generate AskReddit posts using AI~~

## Credits

Christian Robertson for providing the **Roboto** font, used for generating the images of the post/comments, licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

All the YouTubers making those generic shi- \**ahem*\* great AskReddit videos for inspiring me to write this script.
