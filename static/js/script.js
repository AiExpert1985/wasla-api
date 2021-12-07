let gates = true;
document.querySelector('#consider-gates').addEventListener("change", (event)=> gates = event.target.checked);

let drivers_file;
let drivers;
document.querySelector('#drivers').addEventListener("change", (event) => {
    drivers_file = event.target.files;
    let drivers_reader = new FileReader();
    drivers_reader.readAsBinaryString(drivers_file[0]);
    drivers_reader.onload = (event)=>{
        let drivers_data = event.target.result;
        let drivers_workbook = XLSX.read(drivers_data,{type:"binary"});
        let drivers_rowObject = XLSX.utils.sheet_to_row_object_array(drivers_workbook.Sheets[drivers_workbook.SheetNames[0]]);
        drivers = JSON.stringify(drivers_rowObject,undefined,4);
    }
});

let students_file;
let students;
document.querySelector('#students').addEventListener("change", (event) =>{
    students_file = event.target.files;
    let students_reader = new FileReader();
    students_reader.readAsBinaryString(students_file[0]);
    students_reader.onload = (event)=>{
        let students_data = event.target.result;
        let students_workbook = XLSX.read(students_data,{type:"binary"});
        let students_rowObject = XLSX.utils.sheet_to_row_object_array(students_workbook.Sheets[students_workbook.SheetNames[0]]);
        students = JSON.stringify(students_rowObject,undefined,4);
     }
});

document.querySelector('#post').addEventListener("click", () => {
    let api_key = "ksdjf34234a23423"
    let data = {"drivers": drivers,
                "students": students,
                "consider_gates": gates,
                "api_key": api_key,
    };
    fetch('/algorithm', {
      method: 'POST',
      headers: {
        'Content-Type': "application/json; charset=UTF-8"
      },
      body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => console.log('Success:', result))
    .catch((error) => console.error('Error:', error));
});





