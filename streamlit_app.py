import streamlit as st
import json
from datetime import datetime
from agent_openrouter import create_agent

# Page config
st.set_page_config(
    page_title="Strasia Sales Agent Test",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state
if 'agent' not in st.session_state:
    with st.spinner("🤖 Initializing sales agent..."):
        st.session_state.agent = create_agent()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'session_id' not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# Sidebar
st.sidebar.title("🤖 Sales Agent Controls")
st.sidebar.markdown("---")

# Agent status
if st.session_state.agent.knowledge:
    st.sidebar.success("✅ Knowledge Base: Active")
else:
    st.sidebar.warning("⚠️ Knowledge Base: Not Available")

st.sidebar.markdown(f"**Session ID:** {st.session_state.session_id}")
st.sidebar.markdown(f"**Messages:** {len(st.session_state.messages)}")

# Clear conversation
if st.sidebar.button("🗑️ Clear Conversation"):
    st.session_state.messages = []
    st.session_state.agent.clear_memory()
    st.rerun()

# Knowledge base info
with st.sidebar.expander("📚 Knowledge Base Info"):
    if st.session_state.agent.knowledge:
        st.write("The agent has access to corporate services information for:")
        st.write("• Hong Kong")
        st.write("• Singapore") 
        st.write("• Malaysia")
        st.write("• Thailand")
        st.write("• UK")
        st.write("• USA")
    else:
        st.write("Knowledge base is not available. The agent will use general responses.")

# Test scenarios
with st.sidebar.expander("🧪 Test Scenarios"):
    if st.button("💼 Business Inquiry"):
        test_message = "I'm looking to set up a company in Singapore. What do I need to know?"
        st.session_state.test_message = test_message
        st.rerun()
    
    if st.button("💰 Cost Inquiry"):
        test_message = "How much does it cost to incorporate in Hong Kong and what's the timeline?"
        st.session_state.test_message = test_message
        st.rerun()
    
    if st.button("🌍 Multi-jurisdiction"):
        test_message = "I need to compare incorporation options between UK and Singapore for my tech startup"
        st.session_state.test_message = test_message
        st.rerun()

# Main interface
st.title("🤖 Strasia Sales Agent")
st.markdown("**Professional Corporate Services Consultant**")
st.markdown("---")

# Chat interface
chat_container = st.container()

# Display conversation
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                st.caption(f"*Sent at {message.get('timestamp', 'Unknown time')}*")

# Input handling
user_input = st.chat_input("Type your message here...")

# Handle test message from sidebar
if hasattr(st.session_state, 'test_message'):
    user_input = st.session_state.test_message
    delattr(st.session_state, 'test_message')

if user_input:
    # Add user message
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": "user", 
        "content": user_input,
        "timestamp": timestamp
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent.generate_response(user_input)
                st.markdown(response)
                st.caption(f"*Sent at {datetime.now().strftime('%H:%M:%S')}*")
                
                # Add assistant response to messages
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })

# Conversation analysis
if len(st.session_state.messages) > 0:
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
        st.metric("User Messages", len(user_messages))
    
    with col2:
        assistant_messages = [msg for msg in st.session_state.messages if msg["role"] == "assistant"]
        st.metric("Agent Responses", len(assistant_messages))
    
    with col3:
        # Check if booking was mentioned
        booking_mentioned = any("CALENDLY_LINK" in msg["content"] or "EMAIL" in msg["content"] 
                               for msg in st.session_state.messages if msg["role"] == "assistant")
        st.metric("Booking Offered", "Yes" if booking_mentioned else "No")

# Export conversation
if st.sidebar.button("💾 Export Conversation"):
    conversation_data = {
        "session_id": st.session_state.session_id,
        "timestamp": datetime.now().isoformat(),
        "messages": st.session_state.messages
    }
    
    json_str = json.dumps(conversation_data, indent=2)
    st.sidebar.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name=f"conversation_{st.session_state.session_id}.json",
        mime="application/json"
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <small>Sales Agent Test Interface | OpenRouter + Claude 3.5 Sonnet</small>
    </div>
    """,
    unsafe_allow_html=True
)