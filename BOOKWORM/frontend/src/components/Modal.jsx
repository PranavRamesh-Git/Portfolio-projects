function Modal({bookDetails,onClose}){
    if (!bookDetails){
        return null;
    }
    return (
        <div className="modal open" id="view-modal">
            <div class="view-modal">
                <p>DESCRIPTION :</p>
                <p className="summary" id="summary">{bookDetails}</p>
                <button type="button" id="close-modal" onClick={onClose}>CLOSE</button>
            </div>
        </div>    
    );

}
export default Modal;