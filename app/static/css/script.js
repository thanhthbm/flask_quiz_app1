//
// // Function to add a new question group
// function addQuestions() {
//     // Check if a subject is selected
//     const subject = document.getElementById("subject");
//     if (!subject.value) {
//         alert("Vui lòng chọn môn học trước khi thêm câu hỏi.");
//         return;
//     }
//
//     // Select the form element
//     const form = document.getElementById("question-form");
//
//     // Create a new question group container
//     const questionGroup = document.createElement("div");
//     questionGroup.className = "question-group";
//
//     // Add HTML content for a new question and answer options
//     questionGroup.innerHTML = `
//     <div class="form-group">
//         <label for="question">Nội dung câu hỏi</label>
//         <input type="text" name="question[]" required>
//     </div>
//
//     <div class="form-group">
//         <label>Đáp án:</label>
//         <div class="answer-options">
//             <div class="answer-option">
//                 <input type="radio" name="correct_answer[]" value="option1">
//                 <input type="text" name="option1[]" placeholder="Đáp án 1" required>
//             </div>
//             <div class="answer-option">
//                 <input type="radio" name="correct_answer[]" value="option2">
//                 <input type="text" name="option2[]" placeholder="Đáp án 2" required>
//             </div>
//             <div class="answer-option">
//                 <input type="radio" name="correct_answer[]" value="option3">
//                 <input type="text" name="option3[]" placeholder="Đáp án 3" required>
//             </div>
//             <div class="answer-option">
//                 <input type="radio" name="correct_answer[]" value="option4">
//                 <input type="text" name="option4[]" placeholder="Đáp án 4" required>
//             </div>
//         </div>
//     </div>
// `;
//
//
//     // Add the new question group before the submit button
//     form.insertBefore(questionGroup, form.querySelector(".add-question-btn"));
// }
//
// // Function to toggle custom subject input