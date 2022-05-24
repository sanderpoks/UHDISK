from itertools import zip_longest

def order_sequence(sequence:list) -> list:
    return reorder(splice(sequence))



def main():
    testsequence = [1,2,3,4,5,12,13,14,21,22,23,24,25,27,29,30] #Expecting 1-5, 12-14, 21-25, 27, 29-30
    sequence_list = splice(testsequence)
    print(sequence_list)
    reordered_list = reorder(sequence_list)
    print(reordered_list)

def splice(sequence: list) -> list:
    result_list = []
    previous_item = None
    current_list = []
    for i in sequence:
        i = int(i)
        if not previous_item: # First iteration
            current_list.append(i)
            previous_item = i
            continue
        if previous_item:
            if i == previous_item + 1:
                current_list.append(i)
                previous_item = i
                continue
            else:
                result_list.append(current_list.copy())
                current_list = []
                current_list.append(i)
                previous_item = i
                continue
    result_list.append(current_list)
    return result_list

def reorder(sequences: list) -> list:
    final_list = []
    for i in zip_longest(*sequences):
        for a in i:
            if a:
                final_list.append(a)
    return final_list








if __name__ == "__main__":
    main()
