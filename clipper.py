from moviepy.editor import *

# clip = VideoFileClip("test.mp4", audio=True).set_duration(7.51).subclip(2.84)
# # audio = AudioFileClip("test.mp4")
# # clip.audio  = audio.set_duration(7.51).subclip(2.84)
# clip.write_videofile("test-clip.mp4")

def stitchSummaryClips(obj):
    video_clips = []
    for o in obj:
        mainClip = VideoFileClip(o+".mp4", audio=True)
        for i in range(len(obj[o])):
            print(obj[o][i]["duration"])
            endtime = obj[o][i]["start"] + obj[o][i]["duration"]
            clip = mainClip.subclip(obj[o][i]["start"], endtime)
            video_clips.append(clip)
    finalvideo = concatenate_videoclips(video_clips)
    finalvideo.write_videofile('summaryshort.mp4')


def stitchClipFiles(*clips):
    video_clips = []
    for clip in clips:
        video_clips.append(VideoFileClip(clip))
    finalvideo = concatenate_videoclips(video_clips)
    finalvideo.write_videofile('clipstogether.mp4')
