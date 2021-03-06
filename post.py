'''
Library functions for XML_converter.
'''

from __future__ import print_function
import re


def create_uri(id_string, entity_type=None):
    '''
    Creates a new uri from a given string.
    '''

    existing_uris = {
        u'ethernet': u'db:Ethernet',
        u'arduino': u'db:Arduino',
        u'linux': u'db:Linux',
        u'c++': u'db:C++',
        u'wifi': u'db:Wifi'
    }

    if entity_type is None:
        uri = u'sws:{}' .format(id_string)
    elif entity_type == u"Post":
        uri = u'sws:Post{}' .format(id_string)
    else:
        for key in existing_uris.keys():
            if key in entity_type:
                return existing_uris[key]
            else:
                uri = u'sws:{}' .format(id_string)
    return uri

def format_str(string):
    '''
    Takes care of formatting strings to be valid RDF.
    '''
    # Esacpe backslashes.
    string = string.replace('\\', '\\\\')
    # Check for double quotes and escape them.
    string = string.replace('"', '\\"')
    # Remove newlines.
    string = string.replace('\n', '')
    # Prepend/append double quotes.
    string = '"' + string + '"'

    return string


class Post(object):
    '''
    Every post, question or answer, has an Id number and a URI.
    '''

    def __init__(self, attrib_dict):
        self.Id = attrib_dict['Id']
        self.uri = create_uri(self.Id, entity_type=u'Post')

    def _parse(self, attrib_dict):
        '''
        Parses the attribute dictionary into a new
        dictionary that contains only relevant attributes
        where the keys are the predicates, e.g. 'dc:title',
        and the values are the objects, e.g. 'Moby Dick".
        '''

        def parse_tags(tag_string):
            # Input is of the form
            # <ethernet><arduino-yun><web>
            # Parse these elements into a list of strings.
            return re.findall(r'<(.+?)>', tag_string)

        # For question posts, answers are populated after
        #   all answer posts have been instatiated.
        # This attribute is simply ignored for answer posts.
        attribs = {u"sioc:has_reply": []}
        for key,term in self.attrib_to_preds.items():
            if key in attrib_dict.keys():
                pred = term.encode('utf8')
                obj = format_str(attrib_dict[key]).encode('utf8')
                if key == u"Tags":
                    # Find all distinct tags.
                    obj = parse_tags(obj)
                    # Create a URI for each.
                    obj = [create_uri(tag, tag) for tag in obj]
                if key == u"CreationDate":
                    # Get rid of the decimal at the end.
                    obj = re.match(r'(.+)\.\d+', obj).group(1)
                    # Append data type.
                    obj = obj + u'"xsd:dateTime'
                    #print(obj)
                    #raw_input()
                attribs[pred] = obj
        return attribs

    def get_attribs_string(self):
        '''
        Creates a list of SUBJECT-PREDICATE-OBJECT triples
        for the question that can be written out directly.

        Example:
        with open('outfile.ttl', 'w') as out:
            for attrib in question.attribs_strs:
                out.write(attrib)
        '''
        attribs_strs = []
        for pred,obj in self.attribs.items():

            # E.g. 'dc:title' or 'sioc:content'
            if type(obj) == str or type(obj) == unicode:
                # I always want title first for questions.
                if pred == u'dc:title':
                    string = '{0} {1} {2} ;\n' .format('\t', pred, obj)
                    attribs_strs.insert(0, string)
                else:
                    string = '{0} {1} {2} ;\n' .format('\t', pred, obj)
                    attribs_strs.append(string)

            # E.g. 'tsioc:Answer'
            elif type(obj) == list:
                for i in range(len(obj)):
                    # To take care of the cases: obj[i] = Answer | obj[i] = str
                    try:
                        obj_str = obj[i].uri
                    except:
                        obj_str = format_str(obj[i])
                    # Only one reply.
                    if len(obj) == 1:
                        string = '{0} {1} {2} ;\n' .format('\t', pred, obj_str)
                    # First element.
                    elif i == 0:
                        string = '{0} {1} {2},\n' .format('\t', pred, obj_str)
                    # Last element.
                    elif i+1 == len(obj):
                        string = '{0} {1} ;\n' .format('\t\t', obj_str)
                    else:
                        string = '{0} {1},\n' .format('\t\t', obj_str)
                    attribs_strs.append(string)

            # E.g. 'tsioc:BestAnswer'
            elif type(obj) == Answer or type(obj) == Question:
                # I always want has_parent first for answers.
                if pred == u'sioc:has_parent':
                    string = '{0} {1} {2} ;\n' .format('\t', pred, obj.uri)
                    attribs_strs.insert(0, string)
                else:
                    string = '{0} {1} {2} ;\n' .format('\t', pred, obj.uri)
                    attribs_strs.append(string)

        # Make sure last item printed for this URI ends with a full-stop.
        attribs_strs[-1] = attribs_strs[-1][:-2] + '.'

        # Put all RDF class assignments first.
        first_line =  '{0} {1} {2} ;\n' .format(self.uri, "a", u"tsioc:Post")
        attribs_strs.insert(0, first_line)
        second_line = '{0} {1} {2} ;\n' .format('\t', "a", self.type_str)
        attribs_strs.insert(1, second_line)
        if self.type_str == u"tsioc:Answer":
            if self.best_answer:
                third_line = '{0} {1} {2} ;\n' .format('\t', "a", u"tsioc:BestAnswer")
                attribs_strs.insert(2, third_line)

        return attribs_strs


class Answer(Post):

    # Specify which attributes we care about for answer posts.
    attrib_to_preds = {
        u"Body": u"sioc:content",
        u"ParentId" : u"sioc:has_parent",
        u"CreationDate": u"dc:date"
    }

    def __init__(self, attrib_dict):
        Post.__init__(self, attrib_dict)
        self.parent_Id = attrib_dict['ParentId']
        self.attribs = self._parse(attrib_dict)
        self.type_str = u"tsioc:Answer"
        # Is assigned True if this answer is also the 
        # best answer to some question.
        self.best_answer = False


class Question(Post):

    # Specify which attributes we care about for question posts.
    attrib_to_preds = {
        u"Title": u"dc:title",
        u"Body": u"sioc:content",
        u"CreationDate": u"dc:date",
        u"Tags": u"sioc:topic"
    }

    def __init__(self, attrib_dict):
        Post.__init__(self, attrib_dict)
        self.attribs = self._parse(attrib_dict)
        self.type_str = u"tsioc:Question"
        try:
            self.best_answer_Id = attrib_dict[u"AcceptedAnswerId"]
        except:
            self.best_answer_Id = None
