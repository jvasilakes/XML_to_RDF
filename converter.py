#! /usr/bin/env python2.7

#############################################
#                                           #
# Python converter from Stack Exchange XML  #
#    data dump to RDF turtle/Notation3.     #
#         Author: Jake Vasilakes            #
#                                           #
#############################################

from __future__ import print_function

import sys
import xml.etree.ElementTree as ET

# Local import
import post

data_file = "Posts.xml"

rdf_header = u'''@prefix dc: <http://purl.org.dc/elements/1.1/> .
@prefix sioc: <http://rdfs.org/sioc/ns#> .
@prefix tsioc: <http://rdfs.org/sioc/types#> .
'''

def main():

    # Parse the xml file into a Python object.
    tree = ET.parse(data_file)
    root = tree.getroot()

    # Separate posts into questions and answers.
    # Classify based on existence of 'AnswerCount' (questions)
    #   or 'ParentId' (answers). If neither, skip it (there are
    #   some random posts that aren't either.
    questions = []
    answers = []
    for child in root:
        # Add child.attrib because we only need to use
        # the attribute dictionary.
        if 'AnswerCount' in child.attrib.keys():
            questions.append(post.Question(child.attrib))
        elif 'ParentId' in child.attrib.keys():
            answers.append(post.Answer(child.attrib))
        # Neither question nor answer.
        else:
            pass

    # Match up questions and answers.
    for a in answers:
        for q in questions:
            # Check to which question this is an answer.
            if a.parent_Id == q.Id:
                q.attribs[u"tsioc:Answer"].append(a)
                a.attribs[u"sioc:has_parent"] = q
                # Check if this is the best answer to that question.
                try:
                    # Quotes around a.Id are needed for a valid comparison.
                    if '"' + a.Id + '"' == q.attribs[u"tsioc:BestAnswer"]:
                        q.attribs[u"tsioc:BestAnswer"] = a
                except:
                    pass

    # Write some turtle!
    # See notes.txt for what I have to change about this.
    with open("outfile.ttl", "w") as outfile:

        # First write the header.
        outfile.write(rdf_header + '\n')

        for q in questions[:5]:
            for attrib in q.get_attribs_string():
                outfile.write(attrib)
            outfile.write('\n')

        for a in answers[:5]:
            for attrib in a.get_attribs_string():
                outfile.write(attrib)
            outfile.write('\n')


if __name__ == '__main__':
    main()
