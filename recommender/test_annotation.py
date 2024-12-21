from recommender import DoctorRecommender
import torch
from transformers import BertTokenizer, BertForSequenceClassification

def main():
    dr = DoctorRecommender().from_pretrained()
    quotes = [
        # 0ad5285f-4d5b-4046-9de7-bb7cc12b1096-Provider-diarized.txt
        "So then she's going to need the refill.",
        "So then you need refill.",
        "So then she's going to need to refill.",
        "We'll send another vial and then we'll do 0.2. ",
        "Keep doing the three for what you got. And when you're done with that, when you get the new vial, we're going to do 0.2. And there is, I want to say I'm going to look here. The new vials are like 6.25 mls, I think. So let's see here. This is 2. . . Oh, it's 2.5 mL.  ",
        "So that's where we'll send the prescription for the gel. ",
        "And then when you're checking out upfront, they'll have the supplements for you.",
        # 32fe9d76-633d-4736-bc15-967acc004b9b-Visit-diarized
        # Nothing
        # dfb81c0e-c27a-41b8-b68b-226f3a23d17d-Exam-diarized.txt
        " And do you need to refill on the gabapentin?",
        "Do you need a refill on the muscle relaxant, the robaxin?",
        "Because ahead on your refill, so that should give you a little break.",
        # 53e524f5-2704-47c9-8727-347dc42e913e-Visit-diarized
        "So let me refer you for therapy.",
        "i was suggesting the course with the prozac for now", 
        # 760df2cc-fdb0-425f-8333-b70e1bc22539-Visit-diarized
        "We'll order the Rituxan and kind of go from there and just continue to keep tabs on you, but I know it's slow, but it's, again, but I'll be honest. ",
        # 6685dc85-ad0f-4ceb-8039-580ebe1a2d48-Visit-diarized
        # "He doesn't have any energy. He just needs to go back to work. So probably just the HT. ", # Krysta is not sure of HT
        " maybe Texas at least. I mean, it looks like Walgreens is like $40 for it would be a three-month supply. ",
        #  f48983ee-93c4-41bd-9a08-9d6dd442cd01-Visit-diarized
        # Nothing
        #  9b60f5c4-ece1-466b-9b96-1f6cc0371ef0-Wellness_Coach-diarized
        "So I do find that for our athletes, twice a week, subcutaneous testosterone, you get a little bit better performance out of. And so that's probably what I would do is instead of doing the once a week intramuscular injection, we'll do subcutaneous like a B12 shot twice a week.",
        # b5ae558c-6087-47c0-a787-1b639e48e906-Exam-diarized
        "I can start giving you prescriptions, okay?",
        "We will also the prescriptions would be progesterone testosterone and then you talked about the ARE two 90",
        # 1ede56b1-1c04-437c-93c2-4f853ae3aeb2-Visit-diarized
        "So for testosterone and estrogen, you've got some options. You can do or yes, testosterone, estrogen. You can do pellets, which are every three to four months, ",
        "You can also do daily tablets that you take. Or you can do creams.",
        "With progesterone, the only other hormone, that one's always an oral tablet that you take before you go to bed",
        "You will do vitamin supplements for the vitamin D and the B ",
        "I think I would just go ahead and go with the pellets and getting the other tablets for y'all.",
        "And we will order the progesterone for you. ",
        #690c9783-8f58-41d6-9c40-1f21017c16ca-Visit-diarized
        "Take the yeast infection pill, wait for the call from you guys after you contact the insurance for the surgery. ",
        "Take the yeast infection pill",
        #9eef913b-a6b9-4dda-9341-5d3ec036f1be-Visit-diarized
        "here are options for estrogen replacement to that area",
        "There are certain over-the-counter kind of recommendations we can make as far as different supplements that can sometimes help if you're looking at avoiding hormones.",
        #e0e569e3-35ec-4ff7-a738-01abc312d574-Visit-diarized
        "Tell me what are your thoughts on doing some physical therapy for balance?", #Pathient mention, so it seems borderline
        "Let's get that set up and again, they can always spread it out to once a week, ",
        # 2aba7391-0e7c-4790-94d9-61b9e0de9e33-Visit-diarized
        # Nothing
        # 47cc64c1-7f27-4205-a386-9fd4a701f39b-Visit-diarized
        # "And are you doing okay with your testosterone at home still? ",
        "And are you doing okay with your drug at home still? ",
        "I think probably shortly I'll need more. ",
        "I think probably shortly you'll need more. ",
        "But you probably have a refill at the pharmacy. ",
        # "I know you just started the Semaglutag not that long ago.", 
        "I know you just started the drug not that long ago.", 
        "Which is how you have to titrate up. So you probably won't notice any side effects for a while. Hopefully, you won't have that issue ever, but it's more common to happen after the six-week point.",
        #32fe9d76-633d-4736-bc15-967acc004b9b-Visit-diarized.txt
        # Nothing

    ]
    predict = dr.predict(quotes)
    mismatch = 0
    print("Recommendation | Quote \n ==============================================")
    for index, quote in enumerate(quotes):
        answer = 'yes' if predict[index] == 1 else 'no'
        print(answer, " \t| ", quote)
        if predict[index] == 0:
            mismatch += 1
    
    print("# of mismatch : ", mismatch, " out of total : ", index)


if __name__ == '__main__':
    main()