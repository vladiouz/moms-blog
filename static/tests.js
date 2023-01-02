let tests = document.querySelectorAll('.test');

for(let i = 0; i < tests.length; i++)
{
    let category = tests[i].querySelector('h5').innerHTML;

    switch (category)
    {
        case 'Chimie':
            tests[i].classList.add('chimie');
            break;
        case 'Lingvistica':
            tests[i].classList.add('lingvistica');
            break;
        case 'Arte':
            tests[i].classList.add('arte');
            break;
        default:
            tests[i].classList.add('green-bg');
    }
}
