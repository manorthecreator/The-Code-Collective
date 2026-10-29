document.addEventListener("DOMContentLoaded", () => {
  const methodInputs = document.querySelectorAll('input[name="payment_method"]');
  const methodCards = document.querySelectorAll(".method-card");
  const cardFields = document.getElementById("card-fields");
  const cardInputs = cardFields.querySelectorAll("input");
  const form = document.getElementById("payment-form");
  const confirmation = document.getElementById("confirmation");
  const buttonText = document.getElementById("button-text");

  function updateMethod() {
    const cardSelected = document.getElementById("card").checked;
    cardFields.hidden = !cardSelected;
    cardInputs.forEach(input => input.required = cardSelected);
    methodCards.forEach(label => {
      label.classList.toggle("selected", label.querySelector("input").checked);
    });
    buttonText.textContent = cardSelected ? "Place demo order" : "Confirm cash on delivery";
  }
  methodInputs.forEach(input => input.addEventListener("change", updateMethod));

  const numberInput = document.getElementById("card-number");
  numberInput.addEventListener("input", () => {
    const digits = numberInput.value.replace(/\D/g, "").slice(0, 16);
    numberInput.value = digits.replace(/(\d{4})(?=\d)/g, "$1 ");
  });
  document.getElementById("expiry").addEventListener("input", event => {
    let value = event.target.value.replace(/\D/g, "").slice(0, 4);
    if (value.length > 2) value = value.slice(0, 2) + "/" + value.slice(2);
    event.target.value = value;
  });
  document.getElementById("cvv").addEventListener("input", event => {
    event.target.value = event.target.value.replace(/\D/g, "").slice(0, 4);
  });

  form.addEventListener("submit", event => {
    event.preventDefault();
    const chosen = document.querySelector('input[name="payment_method"]:checked').value;
    confirmation.hidden = false;
    confirmation.textContent = chosen === "card"
      ? "Demo order placed successfully! No payment was taken and no card details were sent to a server."
      : "Cash on delivery selected. Your demo order is confirmed; no real order was submitted.";
    confirmation.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
  updateMethod();
});
