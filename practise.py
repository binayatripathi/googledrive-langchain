from flask import Flask
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import GoogleDriveLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
import pinecone
load_dotenv('.env.local')
import os
import new
app = Flask(__name__)
  
# @app.route('/folderId', methods=['GET'])
def get_data(question,docs_id:str):
  # folder_id = request.args.get('folder_id') 
  # question = request.args.get('question')
  print(docs_id)
  pinecone.init(
    api_key=os.environ.get('PINECONE_API_KEY'),
    environment="asia-southeast1-gcp-free")
  SCOPES = ['https://www.googleapis.com/auth/drive']
  try:
    loader = GoogleDriveLoader(
            # folder_id='1QNIzSt6iyVygxx2JepHxjUWGX8LTdEUQ',
            file_ids=[docs_id],
            credentials_path='.creadentials/creadentials.json',
            token_path='.creadentials/token.json',
            recursive=False,
            # file_types=['document']
        )
    docs = loader.load()
    print(docs)
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000, chunk_overlap=0, separators=[" ", ",", "\n"]
            )

    texts = text_splitter.split_documents(docs)
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get('APP_OPENAI_KEY'))
    index_name = "langchain"
    db = Pinecone.from_documents(texts, embeddings,index_name= index_name)
    print('--------->')
    retriever = db.as_retriever()
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo",openai_api_key=os.environ.get('APP_OPENAI_KEY'))
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

    while True:
        if question:
            query = question
            answer= qa.run(query)
            print('---------->',answer)
            return answer
  except Exception as e:
      print(e)
  return 'Nothing'

# get_data("what is this file about")



    
      
      