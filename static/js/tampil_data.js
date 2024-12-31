// Mendapatkan data karyawan dari server
function getData() {
  fetch("/api/data")
    .then((response) => response.json())
    .then((data) => {
      // Memanggil fungsi untuk menampilkan data dalam tabel
      renderTable(data);
    })
    .catch((error) => console.error("Error:", error));
}

// Menampilkan data dalam tabel
function renderTable(data) {
  const tableBody = document.getElementById("data-body");
  tableBody.innerHTML = "";

  data.forEach((item) => {
    const row = document.createElement("tr");
    row.innerHTML = `
            <td>${item.name}</td>
            <td>${item.id_karyawan}</td>
        `;
    tableBody.appendChild(row);
  });
}

// Memanggil fungsi getData saat halaman dimuat
document.addEventListener("DOMContentLoaded", getData);
