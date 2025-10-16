import streamlit as st

st.set_page_config(page_title="Secrets Debugger", layout="centered")

st.title("Secrets File Debugger 🕵️")

st.info("This app will show exactly what Streamlit is reading from your secrets file.")

# Check if the secrets object has any keys at all
if st.secrets:
    st.success("✅ Secrets file was found!")
    
    # Try to display the entire secrets dictionary
    try:
        st.write("Here is the content of the secrets file:")
        st.json(st.secrets.to_dict())
    except Exception as e:
        st.error(f"Could not display secrets content. Error: {e}")

else:
    st.error("❌ No secrets file was found or it is empty.")
    st.warning(
        "Please ensure the file exists at the path `.streamlit/secrets.toml` "
        "in your GitHub repository and that it is not empty."
    )
