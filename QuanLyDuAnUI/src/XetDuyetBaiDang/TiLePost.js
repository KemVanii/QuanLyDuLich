import React, { useState, useEffect } from 'react';

const highlightSensitiveWords = (text, sensitiveWords) => {
    let highlightedText = text;

    sensitiveWords.forEach(word => {
        const regex = new RegExp(`\\b${word}\\b`, 'gi');
        highlightedText = highlightedText.replace(regex, `<span class="highlight">${word}</span>`);
    });

    // Trả về chuỗi đã được highlight, sẵn sàng để render trong JSX
    return highlightedText;
};

const PostInfoTable = ({ title, content, sensitiveContentProbabilities }) => {
    const [titleReadability, setTitleReadability] = useState(0);
    const [contentReadability, setContentReadability] = useState(0);
    const [totalReadability, setTotalReadability] = useState(0);
    const [totalReadabilityStatus, setTotalReadabilityStatus] = useState('');
    const [totalReadabilityColor, setTotalReadabilityColor] = useState('green');

    useEffect(() => {
        if (sensitiveContentProbabilities) {
            const titleRead = sensitiveContentProbabilities.title * 100;
            const contentRead = sensitiveContentProbabilities.content * 100;
            setTitleReadability(titleRead);
            setContentReadability(contentRead);
            const newTotalReadability = (titleRead + contentRead) / 2;
            setTotalReadability(newTotalReadability);

            if (titleRead > 70 || contentRead > 70) {
                setTotalReadabilityStatus('(Cảnh báo: Bài viết cần hủy)');
                setTotalReadabilityColor('red');
            } else if (titleRead > 60 || contentRead > 60) {
                setTotalReadabilityStatus('(Xem xét: Bài viết cần xem xét)');
                setTotalReadabilityColor('orange');
            } else {
                setTotalReadabilityStatus('(Bài viết mức độ tốt)');
                setTotalReadabilityColor('green');
            }
        }
    }, [sensitiveContentProbabilities]);

    return (
        <div className="container">
            <h2 className="my-4">Thông tin kiểm tra bài viết</h2>
            <table className="table table-bordered">
                <tbody>
                    <tr>
                        <th>Tiêu đề</th>
                        <td>
                            {/* Sử dụng dangerouslySetInnerHTML với highlightSensitiveWords */}
                            <div dangerouslySetInnerHTML={{ __html: highlightSensitiveWords(title, sensitiveContentProbabilities.sensitive_title) }} />
                        </td>
                    </tr>
                    <tr>
                        <th>Tỷ lệ tiêu đề</th>
                        <td style={{ color: titleReadability > 60 ? 'red' : 'green' }}>
                            {titleReadability.toFixed(2)}% {titleReadability > 60 ? '(Cảnh báo: Tiêu đề chứa từ nhạy cảm)' : '(Tiêu đề mức độ tốt)'}
                        </td>
                    </tr>
                    <tr>
                        <th>Nội dung</th>
                        <td>
                            {/* Sử dụng dangerouslySetInnerHTML với highlightSensitiveWords */}
                            <div dangerouslySetInnerHTML={{ __html: highlightSensitiveWords(content, sensitiveContentProbabilities.sensitive_content) }} />
                        </td>
                    </tr>
                    <tr>
                        <th>Tỷ lệ nội dung</th>
                        <td style={{ color: contentReadability > 60 ? 'red' : 'green' }}>
                            {contentReadability.toFixed(2)}% {contentReadability > 60 ? '(Cảnh báo: Nội dung chứa từ nhạy cảm)' : '(Nội dung mức độ tốt)'}
                        </td>
                    </tr>
                    <tr>
                        <th>Tổng tỷ lệ bài viết</th>
                        <td style={{ color: totalReadabilityColor }}>
                            {totalReadability.toFixed(2)}% {totalReadabilityStatus}
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    );
};

export default PostInfoTable;
