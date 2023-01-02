let posts = document.querySelectorAll('.post');

for(let i = 0; i < posts.length; i++)
{
    let category = posts[i].querySelector('h5').innerHTML;

    switch (category)
    {
        case 'Chimie':
            posts[i].classList.add('chimie');
            break;
        case 'Lingvistica':
            posts[i].classList.add('lingvistica');
            break;
        case 'Arte':
            posts[i].classList.add('arte');
            break;
        default:
            posts[i].classList.add('green-bg');
    }
}
