import streamlit as st
import pandas as pd
import requests
import json

def chat_with_csv(df, query):
    
    prompt = prepare_prompt(df, query)
    
    response = requests.post(
        "http://localhost:11434/api/generate",  
        json={
            "model": "llama3",  
            "prompt": prompt,
            "system": "You are a helpful assistant."
        },
        stream=True  
    )

    
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"

    
    result = []
    try:
        for line in response.iter_lines():
            if line:
                json_line = line.decode('utf-8')
                try:
                    data = json.loads(json_line)  
                    if data.get('done'):
                        break
                    result.append(data.get('response', ''))
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        return "Error in response format"

    return ''.join(result)

def prepare_prompt(df, query):
    
    df_str = df.to_string(index=False)  
    return f"Here is the data:\n{df_str}\n\n{query}"


st.set_page_config(layout='wide')


st.title("Multiple-CSV ChatApp powered by LLM")

input_csvs = st.sidebar.file_uploader("Upload your CSV files", type=['csv'], accept_multiple_files=True)

if input_csvs:
   
    selected_file = st.selectbox("Select a CSV file", [file.name for file in input_csvs])
    selected_index = [file.name for file in input_csvs].index(selected_file)

    
    st.info("CSV uploaded successfully")
    data = pd.read_csv(input_csvs[selected_index])
    st.dataframe(data, use_container_width=True)

    
    st.info("Chat Below")
    input_text = st.text_area("Enter the query")

    
    if input_text:
        if st.button("Chat with csv"):
            st.info("Your Query: " + input_text)
            result = chat_with_csv(data, input_text)
            st.success(result)
