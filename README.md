# Data Storytelling
### HPC Hardware Failure Analysis
ECS 272 Information Visualization Final Project

### About
Data story visualizing high-performance computer (HPC) node behavior and analyzing system effects of hardware failure.

### Data
The dataset used is from the K computer at Riken Center for Computational Science (R-CCS). It contains one day of data from 864 compute racks. 

### Results
![](/vue-project/src/assets/screenshot-1.png)
![](/vue-project/src/assets/screenshot-2.png)
![](/vue-project/src/assets/screenshot-3.png)

#### Requirements
- Nodejs (v20.10.0)
- Python (v3.9.18)

### Project setup
- Navigate to project folder

        cd vue-project

- Install dependencies
        
        npm install

- Add K computer data file to data/ folder
- Create processed_data/ folder in vue-project/
- Pre-process .csv file

        python3 process_data.py

- Run server

        npm run dev

- Access the visualization by typing in the following url:`http://localhost:5173` in your browser (Chrome preferred)

Authors: Allison Austin, Yu-Chia Huang