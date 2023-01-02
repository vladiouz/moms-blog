let noOfQuestions = document.querySelector('.no-of-q').innerHTML;
let qNumber = document.querySelector('.q-number');
let backButton = document.querySelector('.previous');
let nextButton = document.querySelector('.next');
let questions = document.querySelectorAll('.question');


backButton.addEventListener('click', function ()
{
    if (Number(qNumber.innerHTML) > 1)
    {
        qNumber.innerHTML = Number(qNumber.innerHTML) - 1;
        questions[Number(qNumber.innerHTML) - 1].classList.remove('hidden');
        questions[Number(qNumber.innerHTML)].classList.add('hidden');

        if (Number(qNumber.innerHTML) == 1)
        {
            backButton.classList.add('hidden');
        };

        if (Number(qNumber.innerHTML) + 1 == noOfQuestions)
        {
            nextButton.classList.remove('hidden');
        };

    };
});

nextButton.addEventListener('click', function ()
{
    if (Number(qNumber.innerHTML) < Number(noOfQuestions))
    {
        qNumber.innerHTML = Number(qNumber.innerHTML) + 1;
        questions[Number(qNumber.innerHTML) - 1].classList.remove('hidden');
        questions[Number(qNumber.innerHTML) - 2].classList.add('hidden');

        if (Number(qNumber.innerHTML) == 2)
        {
            backButton.classList.remove('hidden');
        };

        if (Number(qNumber.innerHTML) == noOfQuestions)
        {
            nextButton.classList.add('hidden');
        };

    };
});

