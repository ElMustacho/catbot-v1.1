import nltk
import catunits_catbot
import re
# posts = nltk.corpus.nps_chat.xml_posts()[:10000]
#
names = catunits_catbot.Catunits()
# def dialogue_act_features(post):
#     features = {}
#     for word in nltk.word_tokenize(post):
#         features['contains({})'.format(word.lower())] = True
#     return features
#
# featuresets = [(dialogue_act_features(post.text), post.get('class')) for post in posts]
#
# # 10% of the total data
# size = int(len(featuresets) * 0.1)
#
# # first 10% for test_set to check the accuracy, and rest 90% after the first 10% for training
# train_set, test_set = featuresets[size:], featuresets[:size]
#
# # get the classifer from the training set
# classifier = nltk.NaiveBayesClassifier.train(train_set)
# # to check the accuracy - 0.67
# # print(nltk.classify.accuracy(classifier, test_set))
#
# question_types = ["whQuestion","ynQuestion"]
# def is_ques_using_nltk(ques):
#     question_type = classifier.classify(dialogue_act_features(ques))
#     return question_type in question_types
#
#
# def is_nltk_detect(ques):
#     question_type = classifier.classify(dialogue_act_features(ques))
#     if question_type in question_types:
#         return 0
#     #elif question_type == 'Statement':
#     #    return 1
#     else:
#         return 2
#
# question_pattern = ["do i", "do you", "what", "who", "is it", "why","would you", "how","is there",
#                     "are there", "is it so", "is this true" ,"to know", "is that true", "are we", "am i",
#                    "question is", "tell me more", "can i", "can we", "tell me", "can you explain",
#                    "question","answer", "questions", "answers", "ask"]
#
# helping_verbs = ["is","am","can", "are", "do", "does"]
# # check with custom pipeline if still this is a question mark it as a question
# def is_question(question):
#     question = question.lower().strip()
#     if not is_ques_using_nltk(question):
#         is_ques = 'not a question'
#         # check if any of pattern exist in sentence
#         for pattern in question_pattern:
#             is_ques = pattern in question
#             if is_ques:
#                 break
#
#         # there could be multiple sentences so divide the sentence
#         sentence_arr = question.split(".")
#         for sentence in sentence_arr:
#             if len(sentence.strip()):
#                 # if question ends with ? or start with any helping verb
#                 # word_tokenize will strip by default
#                 first_word = nltk.word_tokenize(sentence)[0]
#                 if sentence.endswith("?") or first_word in helping_verbs:
#                     is_ques = 'detected by extra code'
#                     break
#         return is_ques
#     else:
#         return 'detected by nltk'
# stupid_words=['i just', 'i rolled', 'is it good', 'just got', 'is she good', 'is he good', 'new uber', 'rolled', 'pulled']
#
#
# def is_bc_question(question, limit=3):  # limit means "how many words are required to mark a question as 'stupid bc'"
#     precalc = is_nltk_detect(question)
#     if precalc == 0:
#         pass
#     elif precalc == 1:
#         i = 0
#         for word in stupid_words:
#             if word in question.lower():
#                 i=+1
#         if i > limit:
#             pass
#         else:
#             return []
#     else:
#         return []
#     units_mentioned = []
#     for word in question.split(' '):
#         if len(word) > 3:
#             name=names.getUnitCode(word, 0)
#             if name[0]=='no result' or name[0]=='name not unique':
#                 pass
#             else:
#                 units_mentioned.append(names.getnamebycode(name[0]))
#    return units_mentioned

def is_unit_question_regex(message, errors=0):
    regex_extracted = re.sub(r"^.*(just )?(got|rolled|pulled)\s+([\w ',+]+)\W((is|are)\s+(he|she|it|that|they)|are\s+they)\s+good$",
                            r'\3', message, flags=re.IGNORECASE)
    unit_to_search = names.getUnitCode(regex_extracted, errors)
    if unit_to_search[0] == 'no result' or unit_to_search[0] == 'name not unique' or len(message) == len(
            regex_extracted):
        regex_extracted = re.sub(
            r"^.*how\s+good\s+(are|is)\s+([\w '-]+)\s(on|at|in|as|vs|if|for|with|when|against|compared|versus)[\w '-]+$", r'\1', message, flags=re.IGNORECASE)
        unit_to_search = names.getUnitCode(regex_extracted, errors)
        if unit_to_search[0] == 'no result' or unit_to_search[0] == 'name not unique' or len(message) == len(
                regex_extracted):
            return ''
        else:
            return names.getnamebycode(unit_to_search[0])
    else:
        return names.getnamebycode(unit_to_search[0])
