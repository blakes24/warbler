$(async function() {

    $('.like-form').on('submit', updateLike)
    $('.unlike').on('submit', removeLikedMsg)

})


async function updateLike(e) {
    e.preventDefault();

    const url = $(this).prop('action')
    const msg = $(this).attr('id')

    const res = await axios.post(url)

    if(res.data === "Added") {
        $(this).attr('action', `/users/un_like/${msg}`)
        $(this).children(':button').toggleClass('btn-primary')
        $(this).children(':button').toggleClass('btn-secondary')
    }

    if(res.data === "Removed") {
        $(this).attr('action', `/users/add_like/${msg}`)
        $(this).children(':button').toggleClass('btn-primary')
        $(this).children(':button').toggleClass('btn-secondary')
    }
}
async function removeLikedMsg(e) {
    e.preventDefault();

    const url = $(this).prop('action')
    const res = await axios.post(url)

    if(res.data === "Removed") {
        $(this).parents('li').remove()
    }
}