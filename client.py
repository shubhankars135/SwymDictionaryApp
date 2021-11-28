from redis_server import Redis
from difflib import get_close_matches
import re


def get_possible_edits(word):
    """
    This function returns a set of possible edits to the entered word by deleting, tranposing, replacing
    and inserting only letter at a time
    """

    """
    TODO - We can further assign weights to these edit types e.g. A user usually misses few letters 
    from the intended word, there are higher chances that the intended word will lie in deletes array
    """
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]

    return set(deletes + transposes + replaces + inserts)


def get_closest_words(word, word_list, max_words):   
    """
    Gives closest n words from the list of words to the entered word
    """             
    if len(word_list) > 3:
        return get_close_matches(word, word_list, max_words)
    else:
        return word_list


def create_users_db(username):
    """
    Creates and returns a user specific schema which can be used to further user specific operations
    """
    r = Redis(db=username)
    print("------------Welcome to Dictionary-------------")
    print("type 'exit123' to exit app")
    print("Parsing text file....")
    with open('dictionary.txt', encoding='utf-8', errors='ignore') as text_dict:
        lines = text_dict.readlines()
        for line in lines:
            if line == '\n':
                continue
            li = re.split(r'adj\.|n\.|v\.|pl\.|abbr\.|predic\.|var\.|pron\.|attrib\.', line, maxsplit=1)
            if len(li) > 1:
                word = li[0].replace('—','')
                r.set(word.rstrip().lower(), li[1].rstrip()) 
    print("Loaded text file")
    return r



if __name__ == '__main__':

    def read_input(db_instance=None):
        if db_instance is None:
            username = input('Enter your name\n')
            db_instance = create_users_db(username)

        input_str = input("Enter a word    :").lower()
        if  input_str == 'exit123':
            print('Bye !')
            return
        else:
            output = db_instance.get(input_str) 

            # if the entered word doesn't exists in Dictionary
            if output is None:
                possible_edits = []
                final_three_recommendations = []
                words_remaining = 3

                # looping untill we find three recommendations
                while len(final_three_recommendations) < 3:
                    if possible_edits:
                        ## finding secondary possible edits - i.e replacing, deleteing, adding more letters 
                        ## the original word
                        possible_edits = set(e2 for e1 in possible_edits for \
                            e2 in get_possible_edits(e1))
                    else:
                        ## finding secondary possible edits - i.e replacing, deleteing, adding one letter 
                        ## the original word                        
                        possible_edits = get_possible_edits(input_str)

                    ## finding words available in main dictionary from possible edits
                    available_words = list(db_instance.avaiable_words(possible_edits))

                    ## remove the recommended word from available_words if present
                    for final_word in final_three_recommendations:
                        try:
                            available_words.remove(final_word)
                        except ValueError:
                            print('Does not exist')


                    if available_words is None:
                        # if no valid words are found from the dictionary try with further edits
                        continue                    
                    elif len(available_words) > words_remaining:
                        ## if more than 3 valid words are found from the dictionary
                        ## we'll get the closest three words 
                        closest_3_words = get_closest_words(input_str, available_words, \
                         words_remaining)                    
                        final_three_recommendations.extend(closest_3_words)
                    else:
                        ## if  valid words are found from the dictionary
                        ##  

                        words_remaining = words_remaining - len(available_words)
                        final_three_recommendations.extend(available_words)

                print_str = "Entered word does'nt exist \nPls. select an option fr. following\n"
                for i, final_word in enumerate(final_three_recommendations):
                    print_str += str(i+1) + " " + final_word + "  "
                print(print_str)
                selected_word = int(input())
                output = db_instance.get(final_three_recommendations[selected_word - 1])
                print(output)
            else:
                print(output)
        read_input(db_instance)
    read_input()
