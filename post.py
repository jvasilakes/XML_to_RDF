'''
Library functions for XML_converter.
'''

from __future__ import print_function


def create_uri(id_string):
    '''
    Creates a new uri from an Id number.
    '''
    return u'<http://vocab.inf.ed.ac.uk/sws#{}>' .format(id_string)

def format_str(string):
    '''
    Takes care of formatting strings to be valid RDF.
    '''
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
        self.uri = create_uri(self.Id)

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
            if type(obj) == str:
                string = '{0} {1} {2} .\n' .format(self.uri, pred, obj)
                attribs_strs.append(string)
            # E.g. 'tsioc:Answer'
            elif type(obj) == list:
                for elem in obj:
                    string = '{0} {1} {2} .\n' .format(self.uri, pred, elem.uri)
                    attribs_strs.append(string)
            # E.g. 'tsioc:BestAnswer'
            elif type(obj) == Answer or type(obj) == Question:
                string = '{0} {1} {2} .\n' .format(self.uri, pred, obj.uri)
                attribs_strs.append(string)
                
        return attribs_strs


class Answer(Post):

    def __init__(self, attrib_dict):
        Post.__init__(self, attrib_dict)
        self.parent_Id = attrib_dict['ParentId']
        self.attribs = self._parse(attrib_dict)

    def _parse(self, attrib_dict):

        # Specify which attributes we care about for quesiton posts.
        attrib_to_preds = {
            u"Body": u"sioc:content",
            u"ParentId" : u"sioc:has_parent"
        }

        # The answer list is populated after we create uris
        # for each answer post.
        attribs = {u"tsioc:Answer": []}
        
        for key,term in attrib_to_preds.items():
            if key in attrib_dict.keys():
                pred = term.encode('utf8')
                obj = format_str(attrib_dict[key]).encode('utf8')
                attribs[pred] = obj

        return attribs


class Question(Post):

    def __init__(self, attrib_dict):
        Post.__init__(self, attrib_dict)
        self.attribs = self._parse(attrib_dict)

    def _parse(self, attrib_dict):
        '''
        Parses the attribute dictionary into a new
        dictionary that contains only relevant attributes
        where the keys are the predicates, e.g. 'dc:title',
        and the values are the objects, e.g. 'Moby Dick".
        '''

        # Specify which attributes we care about for quesiton posts.
        attrib_to_preds = {
            u"Title": u"dc:title",
            u"Body": u"sioc:content",
            u"AcceptedAnswerId" : u"tsioc:BestAnswer"
        }

        # The answer list is populated after we create uris
        # for each answer post.
        attribs = {u"tsioc:Answer": []}
        
        for key,term in attrib_to_preds.items():
            if key in attrib_dict.keys():
                pred = term.encode('utf8')
                obj = format_str(attrib_dict[key]).encode('utf8')
                attribs[pred] = obj

        return attribs
