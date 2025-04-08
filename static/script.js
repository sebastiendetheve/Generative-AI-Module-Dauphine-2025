async function processText() {
    const inputText = document.getElementById('inputText').value;
    const companyInput = document.getElementById('companyInput').value;
    const outputText = document.getElementById('outputText');
    
    if (!inputText.trim()) {
        outputText.textContent = 'Please enter some text.';
        return;
    }

    if (!companyInput.trim()) {
        outputText.textContent = 'Please enter a company name.';
        return;
    }

    try {
        console.log('Sending request to GPT model...');
        const response = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                text: inputText,
                company: companyInput
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Network response was not ok');
        }

        console.log('Response received from GPT model');
        outputText.textContent = data.result;
    } catch (error) {
        console.error('Error:', error);
        outputText.textContent = 'Error: ' + error.message;
    }
} 