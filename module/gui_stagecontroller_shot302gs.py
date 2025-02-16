import streamlit as st
from stagecontroller_shot302gs import StageController

# Initialize the stage controller
stage_controller = StageController()

st.title("Stage Controller GUI")

# Axis input
axis = st.number_input("Axis:", min_value=1, max_value=2, step=1)

# Minimum speed input
min_speed = st.number_input("Minimum Speed:", value=2000)

# Maximum speed input
max_speed = st.number_input("Maximum Speed", value=5000)

# Acceleration input
acceleration = st.number_input("Acceleration", value=100)

# Position input
position = st.number_input("Position (um):", min_value=0.0, step=0.1)

# Direction input
direction = st.selectbox("Direction:", ["+", "-"])

# Wait time input
wait_time = st.number_input("Wait Time (s):", min_value=0.0, step=0.1)

# Move button
if st.button("Move"):
    try:
        stage_controller.setSpeed(
            ax1_min_speed=min_speed, ax1_max_speed=max_speed, ax1_acceleration=acceleration,
            ax2_min_speed=min_speed, ax2_max_speed=max_speed, ax2_acceleration=acceleration,
        )
        stage_controller.moveAbs(axis, position, direction, wait_time)
        st.success(f"Moved axis {axis} to position {position} um in direction {direction}")
    except ValueError as e:
        st.error(f"Invalid input: {e}")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Home button
if st.button("Home"):
    try:
        stage_controller.moveToHomePosition(axis)
        st.success("Homed the stage successfully")
    except Exception as e:
        st.error(f"An error occurred while homing: {e}")
