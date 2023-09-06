import LLMProcess as llm

DEFAULT_STRUCTURE = "write the response in a short paragraph."


def ask_from_a_document(question, document, custom_format=DEFAULT_STRUCTURE):
    print("You have asked {0} from {1}".format(question, document))
    resp = llm.answer_query_from_db(question,
                                    custom_format=custom_format,
                                    search_kwargds={"filter": {"source": document}})
    return resp['answer']


def full_results_ask_from_a_document(question, document, custom_format=DEFAULT_STRUCTURE):
    print("You have asked {0} from {1}".format(question, document))
    resp = llm.answer_query_from_db(question,
                                    custom_format=custom_format,
                                    search_kwargds={"filter": {"source": document}})
    return resp


def ask_from_documents(question, documents, custom_format=DEFAULT_STRUCTURE):
    print("You have asked {0} from {1}".format(question, documents))
    search_kwargs = {
        'filters': [
            {'source': doc} for doc in documents
        ]
    }
    resp = llm.answer_query_from_db(question,
                                    custom_format=custom_format,
                                    search_kwargds=search_kwargs)
    return resp['answer']


def ask_from_all_documents(question, custom_format=DEFAULT_STRUCTURE):
    print("You have asked {0} from {1}".format(question, "all documents"))
    resp = llm.answer_query_from_db(question,
                                    custom_format=custom_format)
    return resp['answer']
