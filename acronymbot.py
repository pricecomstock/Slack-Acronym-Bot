@app.route('/ab', methods=['POST'])
def acronym():
    #Open the acronym list file. It will need to be initialized as a file with contents: {}
    acronym_list_file_name = '/home/pricecomstock/slash-selfie/acronyms/acronym_list.json'
    acronym_list_file = open(acronym_list_file_name,'r+b')
    acronym_list_json = json.load(acronym_list_file)
    
    arguments = request.form['text'].split(':',1)
    
    #If arguments work, move on
    if len(arguments) >= 2:
        command = arguments[0].strip(' ').lower()
        cmdarg = arguments[1].strip(' ')
    #Otherwise we give help
    else:
        command = 'help'
        cmdarg = ''
    
    #initialize response builder
    response=''

    #ADD A NEW ACRONYM
    if  command == 'auto' or command == 'add':
        #Check for limited punctuation
        if cmdarg.replace(' ','').replace(',','',1).replace(';','',1).replace(':','',1).replace("'",'',2).isalnum():
            #Get our phrase to create acronym from
            words = cmdarg.split(' ')
            acro_builder=''
            #No one-word acronyms
            if len(words)>1:
                for word in words:
                    acro_builder += word[0]
                acro_builder = acro_builder.upper()
                #Title case
                cmdarg=cmdarg.title()
                
                #Check for duplicates
                if acro_builder in acronym_list_json and cmdarg not in acronym_list_json[acro_builder]:
                    acronym_list_json[acro_builder].append(cmdarg)
                else:
                    acronym_list_json.update([ (acro_builder, [cmdarg] ) ])

                response += 'Added entry:\n' + bold(acro_builder) + ': ' + cmdarg
            else:
                response += 'Cannot add one-word acronyms'
        else:
            response+= 'Alphanumeric characters and spaces only please.'

    #ADD A NEW ACRONYM MANUALLY
    #This one takes both acronym and meaning as arguments
    elif command == 'manual':
        cmdarg=cmdarg.split(':',1)
        #Acronym part must be alphanumeric
        if cmdarg[0].replace(' ','').isalnum():
            if len(cmdarg) == 2 and len(cmdarg[1].split(' ')) > 1 and len(cmdarg[0]) > 1:
                acr=cmdarg[0].upper().strip(' ')
                words=cmdarg[1].title().strip(' ')
                #Check for duplicates
                if acr in acronym_list_json and words not in acronym_list_json[acr]:
                    acronym_list_json[acr].append(words)
                else:
                    acronym_list_json.update([ (acr, [words] ) ])

                response += 'Added entry:\n' + bold(acr) + ': ' + words
            else:
                response+= 'Manual usage: `/ab manual : [acronym] : [meaning]`\nAcronym must be longer than one character. Definition must be longer than one word.'
        else:
            response+='Alphanumeric characters and spaces only in acronym please.'
    
    #DEFINE AN ACRONYM
    elif command == 'def' or command == 'get' or command == 'decode' or command == 'define':
        cmdarg=cmdarg.upper()
        #See how many entries we have
        if cmdarg in acronym_list_json:
            possibilities = len(acronym_list_json[cmdarg])
        else:
            possibilities = 0

        
        if possibilities == 0:
            response+='I do not have any definitions for *' + cmdarg + '*. Consider adding one?'
        elif possibilities == 1:
            response+= bold(cmdarg) + ': ' + acronym_list_json[cmdarg][0]
        else:
            response+='I have multiple entries for ' + bold(cmdarg) + ':\n'
            for possible in acronym_list_json[cmdarg]:
                response+='  -' + italic(possible) + '\n'
    
    #SEARCH FOR ACRONYM OR DEFINITION BY SIMPLE SUBSTRING
    elif command == 'find' or command == 'search':
        #Search term must be 2 characters or more 
        if len(cmdarg) >= 2:
            cmdarg=cmdarg.lower()
            #Look through acronyms
            for x in sorted(acronym_list_json):
                if cmdarg in x.lower():
                    response += bold(x) + ': ' + str(acronym_list_json[x]) + '\n'
            #Look through meanings
            for x in sorted(acronym_list_json):
                for y in acronym_list_json[x]:
                    if cmdarg in y.lower():
                        response += bold(x) + ': ' + y + '\n'
            if response == '':
                response = "I ain't found shit"
        else:
            response = "Please make search terms at least 2 characters."
    
    #WORK IN PROGRESS
    elif command == 'listall':
        ENABLED = True
        if ENABLED == True:
            for x in acronym_list_json:
                response += bold(x) + ':\n'
                for y in acronym_list_json[x]:
                    response+='  -' + y + '\n'
                response +='\n'
            USER_TOKEN='REDACTED'
            requests.post('https://slack.com/api/files.upload', data = {'content':response,'token':USER_TOKEN, 'filename':str(time.time())+'.txt' })
            response = 'See snippet'
        else:
            response = 'That command is not currently enabled.'
    
    #HELP
    else:
        response+='Usage: /ab [command] : [args]\nExamples:\n  `add : phrase to become acronym`\n  `manual : P2BA : phrase to become acronym`\n  `def : ATBP`\n  `find : text`'

    #Write out our new list
    acronym_list_file.truncate(0)
    acronym_list_file.seek(0)
    acronym_list_file.write(json.dumps(acronym_list_json,sort_keys=True, indent=4))
    acronym_list_file.close()

    return jsonify({'response_type':'in_channel','text':response})