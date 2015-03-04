#! /usr/bin/env python2.7

'''
 Python converter from Stack Exchange XML  
    data dump to RDF turtle/Notation3.     
         Author: Jake Vasilakes            
'''


from __future__ import print_function

import sys
import xml.etree.ElementTree as ET

# Local import
import post

try:
    data_file = sys.argv[1]
    sys.stderr.write("Converting {}...\n" .format(data_file))
except:
    sys.stderr.write("Usage: ./converter.py <Posts.xml>\n")
    exit(1)

outfile = "arduino_data.ttl"

rdf_header = u'''@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix sioc: <http://rdfs.org/sioc/ns#> .
@prefix tsioc: <http://rdfs.org/sioc/types#> .
@prefix db: <http://dbpedia.org/resource/> .
@prefix sws: <http://vocab.inf.ed.ac.uk/sws#> .
'''

def main():

    # Parse the xml file into a Python object.
    tree = ET.parse(data_file)
    root = tree.getroot()

    # Separate posts into questions and answers.
    # Classify based on existence of 'AnswerCount' (questions)
    #   or 'ParentId' (answers). If neither, skip it (there are
    #   some random posts that aren't either).
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
                q.attribs[u"sioc:has_reply"].append(a)
                a.attribs[u"sioc:has_parent"] = q
                # Check if this is the best answer to that question.
                try:
                    if a.Id == q.best_answer_Id:
                        a.best_answer = True
                except:
                    pass

    # Write some turtle!
    with open(outfile, "w") as fp:

        # First write the header.
        fp.write(rdf_header + '\n')

        for q in questions:
            for attrib in q.get_attribs_string():
                fp.write(attrib)
            fp.write('\n\n')

        for a in answers:
            for attrib in a.get_attribs_string():
                fp.write(attrib)
            fp.write('\n\n')

    sys.stderr.write("RDF written to {}\n" .format(outfile))


if __name__ == '__main__':
    main()
