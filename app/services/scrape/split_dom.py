### Splits the formatted content in chunks of max 6000 characters per chunk. ###
### We get dom_content array elements chunk with i which starts at 0, up to 0+6000 (i + max_length = 6000) ###
### We then repeat this process with the for loop, in range of 0, to the lenght of the dom_content, in jumps of 6000 ###
### for every itteration. ###

def split_dom_content(dom_content, max_length=6000):
    return [dom_content[i: i + max_length] for i in range(0, len(dom_content), max_length)]

    # For self-reference, this is same as: #
    # chunks = [] #
    # for i in range(0, len(dom_content), max_length) #
    # chunk = dom_content[i: i + max_length] #
    # chunks.append(chunk) #