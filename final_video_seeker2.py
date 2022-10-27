from youtube_transcript_api import YouTubeTranscriptApi
from SimilarSentences import SimilarSentences
from summarizer import Summarizer
from pytube import YouTube
import spacy
from clipper import *
#load core english library
nlp = spacy.load("en_core_web_sm")
videoFilePaths = []

def summarize(*urls):
    video_id_array = []
    print(urls)
    for url in urls:
        print(url)
        yt = YouTube(url)
        videoKey = url.split("=")[1]
        video_id_array.append(videoKey)
        filename = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')[-2].download(output_path='./', filename=videoKey+'.mp4')
        videoFilePaths.append({yt.title: filename})
    #video_id_array = ['N0DhCV_-Qbg', '8N7IHtwruvA', '7YhdqIR2Yzo']
    transcript_dict_array, summary_array, full_text_array = [], [], []
    sentence_dict = {}

    # Get the transcript and full text and put it in arrays
    for video_url in video_id_array:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_url)
        transcript = transcript_list.find_transcript(['en'])
        transcript_dict= transcript.fetch()
        full_text = transcript.translate('en').fetch()[0]['text']
        transcript_dict_array.append(transcript_dict)
        full_text_array.append(full_text)

    # # Print Full text array
    # for full_text in full_text_array:
    #     # print(i)
    #     # print()
    #     pass

    model = Summarizer()

    # Extract Summary from Full Text 
    for full_text in full_text_array:
        result = model(full_text, ratio=0.2)
        summary_array.append(result)

    # Print Summary Array
    # for summary in summary_array:
    #     print(summary)
    #     print()
    #     pass

    # for i in transcript_dict_array:
    #     print(i, end = '\n\n')
    for k in range(len(transcript_dict_array)):
        transcript_dict = transcript_dict_array[k]
        i = 0
        sentence_dict[video_id_array[k]] = {}
        while i < len(transcript_dict):
            j = i
            sentence = ''
            duration = 0
            start = transcript_dict[i]['start']
            while j < len(transcript_dict):
                if (transcript_dict[j]['text'][len(transcript_dict[j]['text'])-1] == '.'):
                    sentence += transcript_dict[j]['text'].replace('\n', ' ').replace('--', ' ')
                    duration += transcript_dict[j]['duration']
                    i=j+1
                    break
                else:
                    sentence += transcript_dict[j]['text'].replace('\n', ' ') + ' '
                    duration += transcript_dict[j]['duration']
                    j+=1
                if j >= len(transcript_dict):
                    break
                print(sentence)
                print(duration)
            sentence_dict[video_id_array[k]][sentence] = {"start": start, "duration": round(duration, 2)} 
            if i ==  len(transcript_dict) - 1:
                print("checkpoint1")
                break
            

    # Print Sentence Disct
    # for i in sentence_dict:
    #     print(sentence_dict[i], end = '\n\n')
    #     pass

    # Create the sentence_dict.txt
    f = open("sentence_dict.json", "w")
    f.write(str(sentence_dict))
    f.close()

    f = open("sentences.txt", "w")
    for video_id in sentence_dict:
        sentence_details = sentence_dict[video_id]
        print(sentence_details, end = '\n\n')
        print(sentence_details.keys(), end = '\n\n')
        for i in list(sentence_details.keys()):

            f.write(str(i + '\n'))
       

    f.close()
    
    # Model for finding similar sentences
    model = SimilarSentences('sentences.txt',"train")
    model.train()
    model = SimilarSentences('model.zip',"predict")

    f = open("similarity_scores.json", "w")

    # Load core english library
    nlp = spacy.load("en_core_web_sm")
    similarity_score_dict = {}
    for i in range(len(summary_array)):
        summary = summary_array[i]
        doc = nlp(summary)
        # Pick the similar sentences and store it in dictionary
        similarity_score_array = []
        for sentence in doc.sents:
            detailed = model.predict(str(sentence), 1, "detailed")
            print((eval(detailed)[0][0]))
            print()
            similarity_score_array.append((eval(detailed)[0][0]))
        similarity_score_dict[video_id_array[i]] = similarity_score_array
        
    # Write the similarity score
    f.write(str(similarity_score_dict))
    final_sentence_details = {}
    for i in similarity_score_dict:
        sentence_details = []
        video_id = i
        similarity_score = similarity_score_dict[video_id]
        
        for j in range(len(similarity_score)):
            if similarity_score[j]['score'] >= 0.65:
                final_sentence = similarity_score[j]['sentence']
                try:
                    print(sentence_dict[video_id][final_sentence])
                    sentence_details.append(sentence_dict[video_id][final_sentence])
                except Exception:
                    pass
                
        final_sentence_details[video_id] = sentence_details
    
    f = open("final_sentence_details.json", "w")
    print(final_sentence_details)
    f.write(str(final_sentence_details))
    f.close()


    stitchSummaryClips(final_sentence_details)
    print("end")

summarize("https://www.youtube.com/watch?v=N0DhCV_-Qbg")