from .models import ProfessionModel, SkillsModel, AbilitiesModel
from django.core.exceptions import ObjectDoesNotExist


class DevelopStat():
    stat = ''
    bonus = ''


class StatDisplay():
    stat = ''
    value = ''


def process_string(string,all_objects,prefix):
    split_string = string.split('\n')
    mandatory =[] # plain text of skills/abilites or whatever that you have to get
    mandatory_modals =[]
    options = [] # plain text of your options
    for line in split_string:
        if line.find(' / ') == -1:
            mandatory.append(line)
            mandatory_modals.append(line)
        else:
            options.append(line)

    # creates radio buttons for options
    counter = 0
    for i, line in enumerate(options, 0):
        counter += 1
        options[i] = options[i].split(' / ')
        for j, choice in enumerate(options[i], 0):
            if choice[-1] == '\r':
                choice = choice[:-1]
            radio = "<label><input required class=\"mr-2\" type=\"radio\" value=\"" + choice.upper() + "\" name=\"" + str(i) + prefix + "\" >" + choice+"</label>"
            options[i][j] = radio
    for i, line in enumerate(options, 0):
        options[i] = ' / '.join(line)  # options are now <input...> name

    # creates modals
    options = '\n'.join(options)

    mandatory_modals = '\n'.join(mandatory_modals)
    query_set=[]  # So I dont have to send all skills / ablilities to html
    for objectt in all_objects:
        if options.find(objectt.name) != -1 or mandatory_modals.find(objectt.name) != 1:
            modal_link = "<a href=\"#\" data-toggle=\"modal\" data-target=\"#" + objectt.slug + "\">" + objectt.name + "</a>"
            options = options.replace(objectt.name, modal_link)
            mandatory_modals = mandatory_modals.replace(objectt.name, modal_link)
            query_set.append(objectt)

    options = options.split('\n')
    if options[0] == '':
        options.pop(0)

    mandatory_modals = mandatory_modals.split('\n')
    if mandatory_modals[0] == '':
        mandatory_modals.pop(0)

    result = [options,counter,mandatory_modals,mandatory,query_set]

    return result


def process_string_dev(string,type):
    split_string = string.replace(' / ', '\n')
    split_string = split_string.split('\n')

    class Obj():
        name = ''
        bonus = None
        obj = ''


    objects_list =[]
    for i,line in enumerate(split_string,0):
        line = line.replace('\r','')
        if line.find(' (') == -1:
            obj = Obj()
            obj.name = line
            try:
                if type == 'skills':
                    a = SkillsModel.objects.get(name=obj.name)
                    obj.obj = a
                else:
                    a = AbilitiesModel.objects.get(name=obj.name)
                    obj.obj = a
                objects_list.append(obj)
            except ObjectDoesNotExist:
                pass

        else:
            line = line.split(' (')
            obj = Obj()
            obj.name = line[0]
            obj.bonus = '(' + line[1]
            try:
                if type == 'skills':
                    a = SkillsModel.objects.get(name=obj.name)
                    obj.obj = a
                else:
                    a = AbilitiesModel.objects.get(name=obj.name)
                    obj.obj = a
                objects_list.append(obj)
            except ObjectDoesNotExist:
                pass

    return objects_list