let drivers_file;
let drivers
document.querySelector('#drivers').addEventListener("change", (event) => drivers_file = event.target.files)
document.querySelector('#upload-drivers').addEventListener("click", () => {
    if(drivers_file){
        let drivers_reader = new FileReader();
        drivers_reader.readAsBinaryString(drivers_file[0]);
        drivers_reader.onload = (event)=>{
            let drivers_data = event.target.result;
            let drivers_workbook = XLSX.read(drivers_data,{type:"binary"});
            let drivers_rowObject = XLSX.utils.sheet_to_row_object_array(drivers_workbook.Sheets[drivers_workbook.SheetNames[0]]);
            drivers = JSON.stringify(drivers_rowObject,undefined,4);
        }
    }
});


let students_file;
let students
document.querySelector('#students').addEventListener("change", (event) => students_file = event.target.files)
document.querySelector('#upload-students').addEventListener("click", () => {
    if(students_file){
        let students_reader = new FileReader();
        students_reader.readAsBinaryString(students_file[0]);
        students_reader.onload = (event)=>{
            let students_data = event.target.result;
            let students_workbook = XLSX.read(students_data,{type:"binary"});
            let students_rowObject = XLSX.utils.sheet_to_row_object_array(students_workbook.Sheets[students_workbook.SheetNames[0]]);
            students = JSON.stringify(students_rowObject,undefined,4);
        }
     }
});


document.querySelector('#post').addEventListener("click", () => {
    let formData = new FormData();
    formData.append('drivers', drivers);
    formData.append('students', students);
    fetch('/test', {body: formData, method: "post"})
    .then(response => response.json())
    .then(data => console.log('Success:', data))
    .catch((error) => console.error('Error:', error));
});






