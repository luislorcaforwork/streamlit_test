import streamlit as st


def calculator():
    # Title
    st.title("🧮 Simple Calculator")

    # User inputs
    num1 = st.number_input("Enter first number", value=0.0, step=1.0)
    num2 = st.number_input("Enter second number", value=0.0, step=1.0)

    # Operation selection
    operation = st.selectbox("Choose operation", ["Add", "Subtract", "Multiply", "Divide"])

    if st.button("Calculate"):
        if operation == "Add":
            result = num1 + num2
            st.success(f"Result: {result}")
        elif operation == "Subtract":
            result = num1 - num2
            st.success(f"Result: {result}")
        elif operation == "Multiply":
            result = num1 * num2
            st.success(f"Result: {result}")
        elif operation == "Divide":
            if num2 != 0:
                result = num1 / num2
                st.success(f"Result: {result}")
            else:
                st.error("Error: Division by zero is not allowed.")
