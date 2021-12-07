document.addEventListener('DOMContentLoaded', function(){
    upload_data();
});

//function upload_data(){
//    const data = { username: 'example' };
//    fetch('/algorithm', {
//      method: 'POST', // or 'PUT'
//      headers: {
//        'Content-Type': 'application/json',
//      },
//      body: JSON.stringify(data),
//    })
//    .then(response => response.json())
//    .then(data => {
//      console.log('Success:', data);
//    })
//    .catch((error) => {
//      console.error('Error:', error);
//    });
//}

function upload_data(){
  fetch('/test')
        .then(response => response.json())
        .then(text => console.log(text.greeting))
}

//function upload_excel_files(url){
//    const formData = new FormData();
//    const photos = document.querySelector('input[type="file"][multiple]');
//
//    formData.append('title', 'My Vegas Vacation');
//    for (let i = 0; i < photos.files.length; i++) {
//      formData.append(`photos_${i}`, photos.files[i]);
//    }
//
//    fetch(`/${url}`, {
//      method: 'POST',
//      body: formData,
//    })
//    .then(response => response.json())
//    .then(result => {
//      console.log('Success:', result);
//    })
//    .catch(error => {
//      console.error('Error:', error);
//    });
//}

let selectedFile;
console.log(window.XLSX);
document.getElementById('input').addEventListener("change", (event) => {
    selectedFile = event.target.files[0];
})

let data=[{
    "name":"jayanth",
    "data":"scd",
    "abc":"sdef"
}]


document.getElementById('button').addEventListener("click", () => {
    XLSX.utils.json_to_sheet(data, 'out.xlsx');
    if(selectedFile){
        let fileReader = new FileReader();
        fileReader.readAsBinaryString(selectedFile);
        fileReader.onload = (event)=>{
         let data = event.target.result;
         let workbook = XLSX.read(data,{type:"binary"});
         console.log(workbook);
         workbook.SheetNames.forEach(sheet => {
              let rowObject = XLSX.utils.sheet_to_row_object_array(workbook.Sheets[sheet]);
              console.log(rowObject);
              document.getElementById("jsondata").innerHTML = JSON.stringify(rowObject,undefined,4)
         });
        }
    }
});