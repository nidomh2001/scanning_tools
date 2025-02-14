import streamlit as st
from stagecontroller_shot302 import StageController

# Initialize the stage controller
stage_controller = StageController()

st.title("Stage Controller GUI")

# Axis input
axis = st.number_input("Axis:", min_value=1, max_value=2, step=1)

# Position input
position = st.number_input("Position (um):", min_value=0.0, step=0.1)

# Direction input
direction = st.selectbox("Direction:", ["+", "-"])

# Wait time input
wait_time = st.number_input("Wait Time (s):", min_value=0.0, step=0.1)

# Move button
if st.button("Move"):
    try:
        stage_controller.moveAbs(axis, position, direction, wait_time)
        st.success(f"Moved axis {axis} to position {position} um in direction {direction}")
    except ValueError as e:
        st.error(f"Invalid input: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Force move to zero position button
if st.button("Force Move to Zero Position"):
    try:
        stage_controller.forceMoveZeroPosition()
        st.success("Moved to zero position")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Move to base position button
if st.button("Move to Base Position"):
    try:
        stage_controller.moveBasePosition()
        st.success("Moved to base position")
    except Exception as e:
        st.error(f"An error occurred: {e}")